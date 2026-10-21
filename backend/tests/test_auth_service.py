from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.application.auth import AuthService, token_hash
from app.application.errors import ApplicationError

CLINIC = UUID("11111111-1111-4111-8111-111111111111")


class MemoryRepository:
    def __init__(self):
        self.professional = {
            "id": "professional-synthetic",
            "email": "test@example.invalid",
            "display_name": "Teste",
            "password": "synthetic",
        }
        self.memberships = ("Tecnologia",)
        self.attempts = {}
        self.sessions = {}
        self.commits = 0

    @contextmanager
    def unit_of_work(self, **_kwargs):
        yield self
        self.commits += 1

    def lock_attempt(self, _key):
        pass

    def get_attempt(self, key):
        return self.attempts.get(key)

    def save_attempt(self, key, failures, first, locked):
        self.attempts[key] = {
            "failures": failures,
            "first_failure_at": first,
            "locked_until": locked,
        }

    def clear_attempt(self, key):
        self.attempts.pop(key, None)

    def find_professionals(self, email):
        return [self.professional] if email == self.professional["email"] else []

    def find_professional(self, professional_id):
        return self.professional if professional_id == self.professional["id"] else None

    def teams(self, _id):
        return self.memberships

    def create_session(self, hashed, professional_id, expires):
        self.sessions[hashed] = (professional_id, expires)

    def session_professional(self, hashed):
        value = self.sessions.get(hashed)
        return value[0] if value and value[1] > datetime.now(UTC) else None

    def delete_session(self, hashed):
        self.sessions.pop(hashed, None)


def service(repo, **kwargs):
    return AuthService(
        repo,
        lambda password, stored: password == "correct" and stored == "synthetic",
        CLINIC,
        kwargs.get("policy", {}),
        kwargs.get("approved", False),
    )


def test_institutional_id_preserved_and_only_hash_stored():
    repo = MemoryRepository()
    token, actor = service(repo).login("test@example.invalid", "correct")
    assert actor.id == repo.professional["id"]
    assert token not in repo.sessions
    assert token_hash(token) in repo.sessions
    assert len(token) >= 43
    assert actor.is_technology and not actor.permissions


def test_failed_attempts_commit_and_sixth_attempt_is_blocked():
    repo = MemoryRepository()
    auth = service(repo)
    for _ in range(5):
        with pytest.raises(ApplicationError) as error:
            auth.login("test@example.invalid", "wrong")
        assert error.value.status_code == 401
    assert repo.commits == 5
    with pytest.raises(ApplicationError) as error:
        auth.login("test@example.invalid", "correct")
    assert error.value.status_code == 429
    assert not repo.sessions


def test_removed_team_revokes_next_session_read():
    repo = MemoryRepository()
    auth = service(repo)
    token, _ = auth.login("test@example.invalid", "correct")
    repo.memberships = ("Outra equipe",)
    with pytest.raises(ApplicationError) as error:
        auth.authenticate(token)
    assert error.value.status_code == 403


def test_expiry_and_logout():
    repo = MemoryRepository()
    auth = service(repo)
    token, _ = auth.login("test@example.invalid", "correct")
    repo.sessions[token_hash(token)] = (
        repo.professional["id"],
        datetime.now(UTC) - timedelta(seconds=1),
    )
    with pytest.raises(ApplicationError) as error:
        auth.authenticate(token)
    assert error.value.status_code == 401
    token, _ = auth.login("test@example.invalid", "correct")
    auth.logout(token)
    with pytest.raises(ApplicationError):
        auth.authenticate(token)


def test_unapproved_policy_never_grants_data_permissions():
    repo = MemoryRepository()
    token, actor = service(repo, policy={"Tecnologia": ["registry:read"]}).login(
        "test@example.invalid", "correct"
    )
    assert not actor.permissions


def test_unrecognized_team_cannot_login_and_unknown_permission_is_dropped():
    repo = MemoryRepository()
    repo.memberships = ("Equipe explicitamente aprovada no teste",)
    with pytest.raises(ApplicationError):
        service(repo).login("test@example.invalid", "correct")
    _, actor = service(
        repo, approved=True, policy={repo.memberships[0]: ["registry:read", "root:all"]}
    ).login("test@example.invalid", "correct")
    assert actor.permissions == frozenset({"registry:read"})
