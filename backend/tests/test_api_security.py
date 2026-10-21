from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api.dependencies import current_actor
from app.core.config import get_settings
from app.domain.access import Actor
from app.main import app

ORIGIN = get_settings().app_origin


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    with TestClient(app) as value:
        yield value
    app.dependency_overrides.clear()


def actor(*, technology=False, permissions=()):
    return Actor(
        "test-professional",
        "Teste",
        "test@example.invalid",
        ("Tecnologia",) if technology else ("Outra",),
        UUID("11111111-1111-4111-8111-111111111111"),
        frozenset(permissions),
    )


def test_health_is_minimal_and_never_cached(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "social-framework"}
    assert "no-store" in response.headers["cache-control"]
    assert response.headers["x-content-type-options"] == "nosniff"


@pytest.mark.parametrize(
    "path",
    [
        "auth/session",
        "tecnologia/conexao",
        "usuarios?busca=Teste",
        "servico-social/cadastros",
        "servico-social/analises/resumo",
    ],
)
def test_anonymous_access_denied(client, path):
    assert client.get("/api/v1/" + path).status_code == 401


@pytest.mark.parametrize("origin", [None, "https://evil.invalid"])
def test_mutations_require_exact_origin(client, origin):
    response = client.post(
        "/api/v1/auth/login",
        headers={"Origin": origin} if origin else {},
        json={"email": "test@example.invalid", "password": "secret"},
    )
    assert response.status_code == 403
    assert "secret" not in response.text


def test_forged_permissions_rejected_and_input_never_echoed(client):
    response = client.post(
        "/api/v1/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "test@example.invalid", "password": "secret", "team": "Tecnologia"},
    )
    assert response.status_code == 422
    assert "secret" not in response.text and "test@example.invalid" not in response.text


def test_body_limit_enforced_without_content_length(client):
    response = client.post(
        "/api/v1/auth/login", headers={"Origin": ORIGIN}, content=iter([b"x" * 9000, b"y" * 9000])
    )
    assert response.status_code == 413


def test_technology_route_denies_regular_user_even_with_admin_header(client):
    app.dependency_overrides[current_actor] = lambda: actor()
    response = client.get("/api/v1/tecnologia/conexao", headers={"X-Team": "Tecnologia"})
    assert response.status_code == 403


def test_technology_does_not_imply_access_to_social_records(client):
    app.dependency_overrides[current_actor] = lambda: actor(technology=True)
    assert client.get("/api/v1/servico-social/cadastros").status_code == 403
    assert client.get("/api/v1/usuarios?busca=Teste").status_code == 403


def test_unimplemented_social_contract_is_unavailable_not_fake_empty(client):
    app.dependency_overrides[current_actor] = lambda: actor(permissions=("registrations:read",))
    response = client.get("/api/v1/servico-social/cadastros")
    assert response.status_code == 503
    assert "items" not in response.json()


def test_database_error_is_sanitized(client, monkeypatch):
    def broken():
        raise OperationalError("SELECT password", {}, Exception("postgresql://secret"))

    monkeypatch.setattr("app.main.check_readiness", broken)
    app.dependency_overrides[current_actor] = lambda: actor(technology=True)
    response = client.get("/api/v1/tecnologia/conexao")
    assert response.status_code == 503
    assert "password" not in response.text and "postgresql" not in response.text


def test_cookie_policy_and_explicit_session_validation(client, monkeypatch):
    class FakeAuth:
        def login(self, *_args):
            return "synthetic-session-token", actor(technology=True)

    monkeypatch.setattr("app.main.auth_service", lambda: FakeAuth())
    response = client.post(
        "/api/v1/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "test@example.invalid", "password": "test"},
    )
    cookie = response.headers["set-cookie"].lower()
    assert response.status_code == 200
    assert "httponly" in cookie and "samesite=strict" in cookie and "path=/" in cookie
    assert "max-age=28800" in cookie
