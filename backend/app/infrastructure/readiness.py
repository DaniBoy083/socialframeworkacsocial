from sqlalchemy import text

from app.infrastructure.database import transaction

REQUIRED = (
    "profissionais_cadastrados",
    "equipes_profissionais",
    "institutional_users",
    "institutional_frameworks",
    "institutional_user_services",
    "ss_sessions",
    "ss_login_attempts",
)


def check_readiness():
    with transaction(readonly=True) as connection:
        names = set(
            connection.execute(
                text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='public' AND table_name = ANY(:names)
        """),
                {"names": list(REQUIRED)},
            ).scalars()
        )
    return {
        "database": "connected",
        "authTablesPresent": set(REQUIRED).issubset(names),
        "identityContractVerified": False,
        "socialRecordsReady": False,
        "storageReady": False,
    }
