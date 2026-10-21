from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import AliasChoices, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.domain.access import LOGIN_TEAMS


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[3] / ".env.local",
        ),
        extra="ignore",
        populate_by_name=True,
    )
    database_url: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "DATABASE_URL",
            "POSTGRES_URL",
            "PSTGRES_DATABASE_URL",
            "PSTGRES_POSTGRES_URL",
            "PSTGRES_POSTGRES_PRISMA_URL",
        ),
    )
    app_origin: str = "http://localhost:3000"
    environment: Literal["development", "test", "production"] = "development"
    social_clinic_id: UUID | None = None
    social_access_policy: dict[str, list[str]] = Field(default_factory=dict)
    social_policy_approved: bool = False
    session_hours: int = Field(default=8, ge=1, le=8)

    @field_validator("social_clinic_id", mode="before")
    @classmethod
    def blank_scope(cls, value):
        return value or None

    @field_validator("social_access_policy")
    @classmethod
    def policy_cannot_expand_login_teams(cls, value):
        if set(value) - LOGIN_TEAMS:
            raise ValueError("A política admite somente as equipes Serviço social e Tecnologia.")
        return value

    @model_validator(mode="after")
    def validate_origin(self):
        origin = urlsplit(self.app_origin)
        if (
            origin.scheme not in {"http", "https"}
            or not origin.hostname
            or origin.path
            or origin.query
            or origin.fragment
            or origin.username
            or origin.password
        ):
            raise ValueError("APP_ORIGIN deve conter apenas protocolo e host, sem barra final.")
        if self.environment == "production" and origin.scheme != "https":
            raise ValueError("Produção exige origem HTTPS.")
        return self

    @property
    def secure_cookies(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
