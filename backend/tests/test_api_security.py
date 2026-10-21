from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api.dependencies import current_actor
from app.application.auth import AuthService
from app.core.config import get_settings
from app.domain.access import Actor
from app.main import app
from tests.fakes import MemoryRepository

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
        ("Tecnologia",) if technology else ("Serviço social",),
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


@pytest.fixture
def institutional_auth(monkeypatch):
    repository = MemoryRepository()
    auth = AuthService(
        repository,
        lambda password, stored: password == "correct" and stored == "synthetic",
        UUID("11111111-1111-4111-8111-111111111111"),
        {},
        False,
    )
    monkeypatch.setattr("app.main.auth_service", lambda: auth)
    monkeypatch.setattr("app.api.dependencies.auth_service", lambda: auth)
    return repository


@pytest.mark.parametrize("team", ["Serviço social", "Tecnologia"])
def test_http_login_and_session_for_each_allowed_team(client, institutional_auth, team):
    institutional_auth.memberships = (team,)
    response = client.post(
        "/api/v1/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "test@example.invalid", "password": "correct"},
    )
    assert response.status_code == 200
    assert response.json()["actor"]["teams"] == [team]
    assert response.json()["actor"]["permissions"] == []
    assert "password" not in response.text
    session = client.get("/api/v1/auth/session")
    assert session.status_code == 200
    assert session.json()["actor"]["id"] == institutional_auth.professional["id"]
    if team == "Serviço social":
        assert client.get("/api/v1/tecnologia/conexao").status_code == 403
    assert client.get("/api/v1/servico-social/cadastros").status_code == 403


@pytest.mark.parametrize("teams", [(), ("Recepção",), ("Administração",), ("Equipe ABA",)])
def test_http_other_teams_cannot_login_by_forging_headers(client, institutional_auth, teams):
    institutional_auth.memberships = teams
    response = client.post(
        "/api/v1/auth/login",
        headers={"Origin": ORIGIN, "X-Team": "Tecnologia"},
        json={"email": "test@example.invalid", "password": "correct"},
    )
    assert response.status_code == 401
    assert "set-cookie" not in response.headers
    assert not institutional_auth.sessions
    assert client.get("/api/v1/auth/session").status_code == 401


@pytest.mark.parametrize("former_team", ["Serviço social", "Tecnologia"])
@pytest.mark.parametrize(
    "path",
    ["auth/session", "usuarios?busca=Teste", "tecnologia/conexao", "servico-social/cadastros"],
)
def test_http_membership_loss_blocks_existing_session_on_every_endpoint(
    client, institutional_auth, former_team, path
):
    institutional_auth.memberships = (former_team,)
    assert (
        client.post(
            "/api/v1/auth/login",
            headers={"Origin": ORIGIN},
            json={"email": "test@example.invalid", "password": "correct"},
        ).status_code
        == 200
    )
    institutional_auth.memberships = ("Administração",)
    response = client.get("/api/v1/" + path)
    assert response.status_code == 401
    assert "no-store" in response.headers["cache-control"]


@pytest.mark.parametrize(
    "extra",
    [
        {"teams": ["Tecnologia"]},
        {"permissions": ["registry:read"]},
        {"clinic_id": "11111111-1111-4111-8111-111111111111"},
    ],
)
def test_login_body_never_accepts_authorization_attributes(client, institutional_auth, extra):
    response = client.post(
        "/api/v1/auth/login",
        headers={"Origin": ORIGIN},
        json={"email": "test@example.invalid", "password": "correct", **extra},
    )
    assert response.status_code == 422
    assert "set-cookie" not in response.headers
    assert not institutional_auth.sessions
