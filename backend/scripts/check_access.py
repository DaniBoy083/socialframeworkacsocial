"""Inspect only policy configuration, team names and table presence; never credentials or members."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app.core.config import get_settings
from app.domain.access import LOGIN_TEAMS
from app.infrastructure.database import transaction


def main():
    try:
        settings = get_settings()
        with transaction(readonly=True) as connection:
            names = set(
                connection.execute(
                    text("SELECT name FROM public.equipes_profissionais WHERE name = ANY(:names)"),
                    {"names": sorted(LOGIN_TEAMS)},
                ).scalars()
            )
            tables = set(
                connection.execute(
                    text(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name = ANY(:names)"
                    ),
                    {"names": ["ss_sessions", "ss_login_attempts"]},
                ).scalars()
            )
        print(
            json.dumps(
                {
                    "readOnly": True,
                    "scopeConfigured": settings.social_clinic_id is not None,
                    "modulePolicyApproved": settings.social_policy_approved,
                    "loginTeams": [
                        {"name": team, "present": team in names} for team in sorted(LOGIN_TEAMS)
                    ],
                    "authTablesPresent": {"ss_sessions", "ss_login_attempts"}.issubset(tables),
                },
                ensure_ascii=False,
            )
        )
    except Exception as error:
        print(json.dumps({"readOnly": True, "available": False, "errorType": type(error).__name__}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
