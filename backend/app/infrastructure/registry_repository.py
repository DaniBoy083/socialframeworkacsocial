from sqlalchemy import text

from app.infrastructure.database import transaction


class PostgresRegistryRepository:
    def search(self, clinic_id, normalized, user_id, offset):
        escaped = normalized.replace("!", "!!").replace("%", "!%").replace("_", "!_")
        with transaction(readonly=True) as connection:
            return (
                connection.execute(
                    text("""
                SELECT id, full_name, birth_date, responsible_contact, version, created_at
                FROM public.institutional_users
                WHERE clinic_id = CAST(:clinic AS uuid)
                AND ((CAST(:id AS uuid) IS NOT NULL AND id = CAST(:id AS uuid))
                    OR (CAST(:id AS uuid) IS NULL AND full_name LIKE :name ESCAPE '!'))
                ORDER BY full_name, id LIMIT 51 OFFSET :offset
            """),
                    {
                        "clinic": clinic_id,
                        "id": user_id,
                        "name": "%" + escaped + "%",
                        "offset": offset,
                    },
                )
                .mappings()
                .all()
            )
