from fastapi import Depends, HTTPException, Request

from app.application.auth import COOKIE_NAME, AuthService
from app.core.config import get_settings
from app.domain.access import Actor
from app.infrastructure.auth_repository import PostgresAuthRepository
from app.infrastructure.passwords import verify_password


def auth_service():
    config = get_settings()
    return AuthService(
        PostgresAuthRepository(),
        verify_password,
        config.social_clinic_id,
        config.social_access_policy,
        config.social_policy_approved,
        config.session_hours,
    )


def current_actor(request: Request) -> Actor:
    return auth_service().authenticate(request.cookies.get(COOKIE_NAME))


def require_permission(permission: str):
    def dependency(actor: Actor = Depends(current_actor)) -> Actor:
        if permission not in actor.permissions:
            raise HTTPException(403, "Você não tem permissão para esta operação.")
        return actor

    return dependency


def technology_actor(actor: Actor = Depends(current_actor)) -> Actor:
    if not actor.is_technology:
        raise HTTPException(403, "Acesso exclusivo da equipe Tecnologia.")
    return actor
