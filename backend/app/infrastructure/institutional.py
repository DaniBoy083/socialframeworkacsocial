import json

from sqlalchemy import text
from sqlalchemy.engine import Connection


def professional_by_email(connection: Connection, email: str):
    return (
        connection.execute(
            text("""
        SELECT id, email, password, display_name
        FROM public.profissionais_cadastrados
        WHERE lower(email) = :email LIMIT 2
    """),
            {"email": email},
        )
        .mappings()
        .all()
    )


def professional_by_id(connection: Connection, professional_id: str):
    return (
        connection.execute(
            text("""
        SELECT id, email, display_name FROM public.profissionais_cadastrados
        WHERE id = :id
    """),
            {"id": professional_id},
        )
        .mappings()
        .first()
    )


def professional_teams(connection: Connection, professional_id: str) -> tuple[str, ...]:
    rows = connection.execute(
        text("""
        SELECT name FROM public.equipes_profissionais
        WHERE professional_ids_json @> CAST(:ids AS jsonb)
    """),
        {"ids": json.dumps([str(professional_id)])},
    )
    return tuple(row.name for row in rows)
