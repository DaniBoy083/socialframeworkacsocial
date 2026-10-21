from time import perf_counter

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.dependencies import (
    auth_service,
    current_actor,
    require_permission,
    technology_actor,
)
from app.application import auth, registry
from app.application.errors import ApplicationError
from app.core.config import get_settings
from app.domain.access import Actor
from app.infrastructure.database import IntegrationUnavailable
from app.infrastructure.readiness import check_readiness
from app.infrastructure.registry_repository import PostgresRegistryRepository
from app.schemas.auth import LoginInput

settings = get_settings()
app = FastAPI(
    title="Social Framework | AC Social",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class SecurityBoundary:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))

        async def safe_send(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend(
                    [
                        (b"cache-control", b"private, no-store"),
                        (b"x-content-type-options", b"nosniff"),
                        (b"referrer-policy", b"no-referrer"),
                        (b"x-frame-options", b"DENY"),
                    ]
                )
            await send(message)

        if scope["method"] not in {"GET", "HEAD", "OPTIONS"}:
            if headers.get(b"origin", b"").decode() != settings.app_origin:
                return await JSONResponse({"detail": "Origem não autorizada."}, 403)(
                    scope, receive, safe_send
                )
            body = bytearray()
            more = True
            while more:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > 16384:
                    return await JSONResponse(
                        {"detail": "Requisição excede o limite permitido."}, 413
                    )(scope, receive, safe_send)
                more = message.get("more_body", False)
            consumed = False

            async def bounded_receive():
                nonlocal consumed
                if not consumed:
                    consumed = True
                    return {
                        "type": "http.request",
                        "body": bytes(body),
                        "more_body": False,
                    }
                return await receive()

            return await self.app(scope, bounded_receive, safe_send)
        return await self.app(scope, receive, safe_send)


app.add_middleware(SecurityBoundary)


@app.exception_handler(RequestValidationError)
async def validation_error(_request, _exception):
    # Pydantic's default detail includes submitted values (including passwords).
    return JSONResponse({"detail": "Verifique os campos informados."}, status_code=422)


@app.exception_handler(SQLAlchemyError)
@app.exception_handler(IntegrationUnavailable)
async def integration_error(_request, _exception):
    return JSONResponse(
        {"detail": "Integração indisponível. Entre em contato com a equipe de Tecnologia."},
        status_code=503,
    )


def serialize_actor(actor: Actor):
    return {
        "id": actor.id,
        "name": actor.name,
        "email": actor.email,
        "teams": actor.teams,
        "permissions": sorted(actor.permissions),
        "isTechnology": actor.is_technology,
    }


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "social-framework"}


@app.post("/api/v1/auth/login")
def login(payload: LoginInput, response: Response):
    token, actor = auth_service().login(payload.email, payload.password)
    response.set_cookie(
        auth.COOKIE_NAME,
        token,
        max_age=settings.session_hours * 3600,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="strict",
        path="/",
    )
    return {"authenticated": True, "actor": serialize_actor(actor)}


@app.get("/api/v1/auth/session")
def session(actor: Actor = Depends(current_actor)):
    return {"authenticated": True, "actor": serialize_actor(actor)}


@app.post("/api/v1/auth/logout")
def logout(request: Request, response: Response):
    auth_service().logout(request.cookies.get(auth.COOKIE_NAME))
    response.delete_cookie(
        auth.COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="strict",
        secure=settings.secure_cookies,
    )
    return {"success": True}


@app.get("/api/v1/usuarios")
def users(
    busca: str = Query(min_length=3, max_length=200),
    offset: int = Query(default=0, ge=0, le=100000),
    actor: Actor = Depends(require_permission("registry:read")),
):
    return registry.search_users(PostgresRegistryRepository(), actor, busca, offset)


@app.get("/api/v1/tecnologia/conexao")
def diagnostics(_actor: Actor = Depends(technology_actor)):
    start = perf_counter()
    result = check_readiness()
    return {
        **result,
        "latencyMs": round((perf_counter() - start) * 1000),
        "accessPolicyApproved": settings.social_policy_approved,
    }


@app.get("/api/v1/servico-social/cadastros")
def registrations(_actor: Actor = Depends(require_permission("registrations:read"))):
    raise HTTPException(
        503, "O módulo de cadastros aguarda a validação institucional da integração."
    )


@app.get("/api/v1/servico-social/analises/resumo")
def analytics(_actor: Actor = Depends(require_permission("analytics:read"))):
    raise HTTPException(503, "As análises estarão disponíveis após a integração dos cadastros.")


@app.exception_handler(ApplicationError)
async def application_error(_request, error):
    return JSONResponse({"detail": error.detail}, status_code=error.status_code)
