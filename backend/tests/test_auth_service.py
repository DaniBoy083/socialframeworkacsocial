from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.application.auth import AuthService, token_hash
from app.application.errors import ApplicationError
from tests.fakes import MemoryRepository

CLINIC = UUID("11111111-1111-4111-8111-111111111111")


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
    assert error.value.status_code == 401


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


@pytest.mark.parametrize(
    "teams", [("Serviço social",), ("Tecnologia",), ("Serviço social", "Tecnologia")]
)
def test_only_institutional_teams_can_login_without_module_permissions(teams):
    repo = MemoryRepository()
    repo.memberships = teams
    token, actor = service(repo).login("test@example.invalid", "correct")
    assert actor.teams == teams
    assert not actor.permissions
    assert service(repo).authenticate(token).id == actor.id


@pytest.mark.parametrize(
    "teams",
    [
        (),
        ("Recepção",),
        ("Administração",),
        ("Equipe ABA",),
        ("Serviço Social",),
        ("serviço social",),
        ("Servico social",),
        ("Serviço social ",),
        ("tecnologia",),
    ],
)
def test_other_or_similar_teams_denied_even_with_configured_permissions(teams):
    repo = MemoryRepository()
    repo.memberships = teams
    policy = {team: ["registry:read", "registrations:read"] for team in teams}
    with pytest.raises(ApplicationError) as error:
        service(repo, approved=True, policy=policy).login("test@example.invalid", "correct")
    assert error.value.status_code == 401
    assert not repo.sessions
    assert repo.attempts[token_hash("test@example.invalid")]["failures"] == 1


@pytest.mark.parametrize("team", ["Serviço social", "Tecnologia"])
def test_allowed_team_still_requires_correct_password(team):
    repo = MemoryRepository()
    repo.memberships = (team,)
    with pytest.raises(ApplicationError) as error:
        service(repo).login("test@example.invalid", "wrong")
    assert error.value.status_code == 401
    assert not repo.sessions


def test_permission_config_cannot_grant_access_via_unrelated_membership():
    repo = MemoryRepository()
    repo.memberships = ("Tecnologia", "Administração")
    _, actor = service(repo, approved=True, policy={"Administração": ["registry:read"]}).login(
        "test@example.invalid", "correct"
    )
    assert not actor.permissions


def test_social_module_permissions_are_separate_and_unknown_permissions_are_dropped():
    repo = MemoryRepository()
    repo.memberships = ("Serviço social",)
    _, actor = service(
        repo, approved=True, policy={"Serviço social": ["registry:read", "root:all"]}
    ).login("test@example.invalid", "correct")
    assert actor.permissions == frozenset({"registry:read"})
    assert not actor.is_technology


def test_removed_social_team_cannot_keep_session_using_unrelated_policy():
    repo = MemoryRepository()
    repo.memberships = ("Serviço social",)
    auth = service(repo, approved=True, policy={"Administração": ["registry:read"]})
    token, _ = auth.login("test@example.invalid", "correct")
    repo.memberships = ("Administração",)
    with pytest.raises(ApplicationError) as error:
        auth.authenticate(token)
    assert error.value.status_code == 401


def test_switch_between_allowed_teams_recomputes_permissions_from_current_membership():
    repo = MemoryRepository()
    repo.memberships = ("Serviço social",)
    auth = service(repo, approved=True, policy={"Serviço social": ["registry:read"]})
    token, _ = auth.login("test@example.invalid", "correct")
    repo.memberships = ("Tecnologia",)
    current = auth.authenticate(token)
    assert current.is_technology and not current.permissions
