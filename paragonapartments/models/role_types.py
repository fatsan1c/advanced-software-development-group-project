"""Role typing and normalization helpers for the user domain."""

from __future__ import annotations

from enum import Enum


class RoleType(str, Enum):
    """Canonical role values used across the application."""

    ADMINISTRATOR = "Administrator"
    MANAGER = "Manager"
    FINANCE_MANAGER = "Finance Manager"
    FRONT_DESK_STAFF = "Front Desk Staff"
    MAINTENANCE_STAFF = "Maintenance Staff"
    UNKNOWN = "Unknown"


_ROLE_ALIASES: dict[str, RoleType] = {
    "administrator": RoleType.ADMINISTRATOR,
    "admin": RoleType.ADMINISTRATOR,
    "manager": RoleType.MANAGER,
    "financemanager": RoleType.FINANCE_MANAGER,
    "finance": RoleType.FINANCE_MANAGER,
    "frontdeskstaff": RoleType.FRONT_DESK_STAFF,
    "frontdesk": RoleType.FRONT_DESK_STAFF,
    "maintenancestaff": RoleType.MAINTENANCE_STAFF,
    "maintenance": RoleType.MAINTENANCE_STAFF,
}


def normalize_role_key(role: str | RoleType | None) -> str:
    """Normalize role text into an alphanumeric key for lookup."""
    if role is None:
        return ""

    role_text = role.value if isinstance(role, RoleType) else str(role)
    return "".join(char for char in role_text.strip().lower() if char.isalnum())


def parse_role(role: str | RoleType | None) -> RoleType:
    """Parse user role text into a canonical RoleType."""
    if isinstance(role, RoleType):
        return role

    normalized_key = normalize_role_key(role)
    return _ROLE_ALIASES.get(normalized_key, RoleType.UNKNOWN)


def role_label(role: str | RoleType | None) -> str:
    """Return display label for a role value while preserving unknown values."""
    if isinstance(role, RoleType):
        return role.value

    parsed = parse_role(role)
    if parsed is not RoleType.UNKNOWN:
        return parsed.value

    if role is None:
        return RoleType.UNKNOWN.value

    role_text = str(role).strip()
    return role_text if role_text else RoleType.UNKNOWN.value
