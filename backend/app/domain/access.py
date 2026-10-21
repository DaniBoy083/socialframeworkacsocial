from dataclasses import dataclass
from uuid import UUID

SOCIAL_SERVICE_TEAM = "Serviço social"
TECHNOLOGY_TEAM = "Tecnologia"
LOGIN_TEAMS = frozenset({SOCIAL_SERVICE_TEAM, TECHNOLOGY_TEAM})

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
        return TECHNOLOGY_TEAM in self.teams


def can_login(teams: tuple[str, ...]) -> bool:
    return not LOGIN_TEAMS.isdisjoint(teams)


def resolve_permissions(
    teams: tuple[str, ...], policy: dict[str, list[str]], approved: bool
) -> frozenset[str]:
    if not approved:
        return frozenset()
    return frozenset(
        permission
        for team in teams
        if team in LOGIN_TEAMS
        for permission in policy.get(team, [])
        if permission in PERMISSIONS
    )
