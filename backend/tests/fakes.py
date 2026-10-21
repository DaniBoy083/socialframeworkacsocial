from contextlib import contextmanager
from datetime import UTC, datetime


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
