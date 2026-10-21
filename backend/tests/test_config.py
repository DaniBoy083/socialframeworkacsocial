import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_blank_scope_is_unconfigured_and_production_requires_https():
    settings = Settings(_env_file=None, social_clinic_id="", environment="development")
    assert settings.social_clinic_id is None
    with pytest.raises(ValidationError):
        Settings(_env_file=None, environment="production", app_origin="http://example.invalid")
    assert Settings(
        _env_file=None, environment="production", app_origin="https://example.invalid"
    ).secure_cookies


def test_cookies_secure_and_policy_never_default_to_authorized():
    settings = Settings(
        _env_file=None, environment="production", app_origin="https://example.invalid"
    )
    assert settings.secure_cookies
    assert not settings.social_policy_approved and settings.social_access_policy == {}


@pytest.mark.parametrize("team", ["Recepção", "Administração", "Equipe ABA", "Serviço Social"])
def test_config_cannot_expand_the_login_allowlist(team):
    with pytest.raises(ValidationError, match="somente as equipes"):
        Settings(
            _env_file=None,
            social_policy_approved=True,
            social_access_policy={team: ["registry:read"]},
        )


def test_config_accepts_only_confirmed_names_for_module_policy():
    policy = {"Serviço social": ["registry:read"], "Tecnologia": []}
    settings = Settings(_env_file=None, social_access_policy=policy)
    assert settings.social_access_policy == policy
