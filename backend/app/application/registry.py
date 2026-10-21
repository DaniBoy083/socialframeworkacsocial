from uuid import UUID

from app.application.errors import ApplicationError
from app.application.ports import RegistryRepository
from app.domain.access import Actor
from app.domain.identity import normalize_identity


def search_users(repository: RegistryRepository, actor: Actor, query: str, offset: int):
    try:
        normalized = normalize_identity(query)
    except ValueError:
        raise ApplicationError(422, "Pesquisa inválida.") from None
    if len(normalized) < 3:
        raise ApplicationError(422, "Informe pelo menos três caracteres.")
    try:
        user_id = str(UUID(query))
    except ValueError:
        user_id = None
    rows = repository.search(str(actor.clinic_id), normalized, user_id, offset)
    return {
        "users": [
            {
                "id": row["id"],
                "name": row["full_name"],
                "birthDate": row["birth_date"],
                "contact": row["responsible_contact"],
                "version": row["version"],
                "createdAt": row["created_at"],
            }
            for row in rows[:50]
        ],
        "hasMore": len(rows) > 50,
    }
