from contextlib import contextmanager

from sqlalchemy import text

from app.infrastructure.database import transaction
from app.infrastructure.institutional import (
    professional_by_email,
    professional_by_id,
    professional_teams,
)


class PostgresAuthWork:
    def __init__(self, connection):
        self.connection = connection

    def lock_attempt(self, key):
        self.connection.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))"),
            {"key": key},
        )

    def get_attempt(self, key):
        return (
            self.connection.execute(
                text(
                    "SELECT failures, first_failure_at, locked_until FROM public.ss_login_attempts WHERE attempt_key=:key FOR UPDATE"
                ),
                {"key": key},
            )
            .mappings()
            .first()
        )

    def save_attempt(self, key, failures, first, locked):
        self.connection.execute(
            text("""
            INSERT INTO public.ss_login_attempts(attempt_key, failures, first_failure_at, locked_until)
            VALUES (:key, :failures, :first, :locked)
            ON CONFLICT (attempt_key) DO UPDATE SET failures=EXCLUDED.failures,
            first_failure_at=EXCLUDED.first_failure_at, locked_until=EXCLUDED.locked_until
        """),
            {"key": key, "failures": failures, "first": first, "locked": locked},
        )

    def clear_attempt(self, key):
        self.connection.execute(
            text("DELETE FROM public.ss_login_attempts WHERE attempt_key=:key"),
            {"key": key},
        )

    def find_professionals(self, email):
        return professional_by_email(self.connection, email)

    def find_professional(self, professional_id):
        return professional_by_id(self.connection, professional_id)

    def teams(self, professional_id):
        return professional_teams(self.connection, professional_id)

    def create_session(self, token_hash, professional_id, expires):
        self.connection.execute(
            text(
                "INSERT INTO public.ss_sessions(token_hash,professional_id,expires_at) VALUES (:hash,:id,:expires)"
            ),
            {"hash": token_hash, "id": professional_id, "expires": expires},
        )

    def session_professional(self, token_hash):
        return self.connection.execute(
            text(
                "SELECT professional_id FROM public.ss_sessions WHERE token_hash=:hash AND expires_at>now()"
            ),
            {"hash": token_hash},
        ).scalar()

    def delete_session(self, token_hash):
        self.connection.execute(
            text("DELETE FROM public.ss_sessions WHERE token_hash=:hash"),
            {"hash": token_hash},
        )


class PostgresAuthRepository:
    @contextmanager
    def unit_of_work(self, *, readonly=False):
        with transaction(readonly=readonly) as connection:
            yield PostgresAuthWork(connection)
