"""Read-only schema inventory. Never selects patient rows or password values."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import text

from app.infrastructure.database import transaction

TABLES = (
    "profissionais_cadastrados",
    "equipes_profissionais",
    "institutional_users",
    "institutional_frameworks",
    "institutional_user_services",
    "institutional_user_events",
    "ss_sessions",
    "ss_login_attempts",
)
try:
    with transaction(readonly=True) as connection:
        rows = (
            connection.execute(
                text("""
            SELECT table_name, column_name, data_type, udt_name, is_nullable
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name = ANY(:tables)
            ORDER BY table_name, ordinal_position
        """),
                {"tables": list(TABLES)},
            )
            .mappings()
            .all()
        )
        print(json.dumps({"readOnly": True, "columns": [dict(row) for row in rows]}, indent=2))
except Exception as error:
    print(json.dumps({"readOnly": True, "available": False, "errorType": type(error).__name__}))
    sys.exit(1)
