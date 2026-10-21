import hashlib
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.application.errors import ApplicationError
from app.application.ports import AuthRepository, AuthWork
from app.domain.access import Actor, resolve_permissions

COOKIE_NAME = "ac_social_ss"


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    def __init__(
        self,
        repository: AuthRepository,
        password_verifier: Callable[[str, str], bool],
        clinic_id: UUID | None,
        policy: dict[str, list[str]],
        approved: bool,
        session_hours: int = 8,
    ):
        self.repository = repository
        self.verify = password_verifier
        self.clinic_id = clinic_id
        self.policy = policy
        self.approved = approved
        self.session_hours = session_hours

    def actor_from(self, work: AuthWork, professional) -> Actor:
        if not self.clinic_id:
            raise ApplicationError(503, "Integração institucional indisponível.")
        teams = work.teams(professional["id"])
        permissions = resolve_permissions(teams, self.policy, self.approved)
        if not permissions and "Tecnologia" not in teams:
            raise ApplicationError(403, "Acesso não autorizado para este serviço.")
        return Actor(
            id=professional["id"],
            name=professional["display_name"],
            email=professional["email"],
            teams=teams,
            clinic_id=self.clinic_id,
            permissions=permissions,
        )

    def login(self, email: str, password: str) -> tuple[str, Actor]:
        if not self.clinic_id:
            raise ApplicationError(503, "Integração institucional indisponível.")
        key = token_hash(email)
        now = datetime.now(UTC)
        actor = None
        token = ""
        with self.repository.unit_of_work() as work:
            work.lock_attempt(key)
            attempt = work.get_attempt(key)
            if attempt and attempt["locked_until"] and attempt["locked_until"] > now:
                raise ApplicationError(429, "Muitas tentativas. Tente novamente em 15 minutos.")
            professionals = work.find_professionals(email)
            professional = professionals[0] if len(professionals) == 1 else None
            valid = self.verify(password, professional["password"] if professional else "invalid")
            if valid:
                try:
                    actor = self.actor_from(work, professional)
                except ApplicationError as error:
                    if error.status_code != 403:
                        raise
                    valid = False
            if not valid:
                failures = (
                    attempt["failures"] + 1
                    if attempt and attempt["first_failure_at"] > now - timedelta(minutes=15)
                    else 1
                )
                first = attempt["first_failure_at"] if attempt and failures > 1 else now
                work.save_attempt(
                    key,
                    failures,
                    first,
                    now + timedelta(minutes=15) if failures >= 5 else None,
                )
            else:
                token = secrets.token_urlsafe(32)
                work.create_session(
                    token_hash(token),
                    actor.id,
                    now + timedelta(hours=self.session_hours),
                )
                work.clear_attempt(key)
        # Only raise after commit, otherwise failed attempts would be rolled back.
        if not valid or actor is None:
            raise ApplicationError(401, "Credenciais ou acesso não autorizados.")
        return token, actor

    def authenticate(self, token: str | None) -> Actor:
        if not token or len(token) > 128:
            raise ApplicationError(401, "Sua sessão expirou. Entre novamente.")
        with self.repository.unit_of_work(readonly=True) as work:
            professional_id = work.session_professional(token_hash(token))
            professional = work.find_professional(professional_id) if professional_id else None
            if not professional:
                raise ApplicationError(401, "Sua sessão expirou. Entre novamente.")
            return self.actor_from(work, professional)

    def logout(self, token: str | None):
        if token:
            with self.repository.unit_of_work() as work:
                work.delete_session(token_hash(token))
