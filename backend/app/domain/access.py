from dataclasses import dataclass
from uuid import UUID

PERMISSIONS = frozenset({"registry:read", "registrations:read", "analytics:read"})


@dataclass(frozen=True)
class Actor:
    id: str
    name: str
    email: str
    teams: tuple[str, ...]
    clinic_id: UUID
    permissions: frozenset[str]

    @property
    def is_technology(self) -> bool:
        return "Tecnologia" in self.teams


def resolve_permissions(
    teams: tuple[str, ...], policy: dict[str, list[str]], approved: bool
) -> frozenset[str]:
    if not approved:
        return frozenset()
    return frozenset(
        permission
        for team in teams
        for permission in policy.get(team, [])
        if permission in PERMISSIONS
    )
