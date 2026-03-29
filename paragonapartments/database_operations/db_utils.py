"""
Repository Utilities - Shared utility functions for repository modules.
"""

from datetime import date

from database_operations.database_context import query_executor
import pages.components.input_validation as input_validation

_ALL_LOCATION_ALIASES = {"all", "all locations", "alllocation", "alllocations"}

_TENANT_NAME_SQL = "t.name AS tenant_name"
_TENANT_FULL_NAME_SQL = "(t.first_name || ' ' || t.last_name) AS tenant_name"
_TENANT_SHORT_NAME_SQL = "(SUBSTR(t.first_name, 1, 1) || '. ' || t.last_name) AS tenant_name"
_TENANT_FALLBACK_SQL = "CAST(t.tenant_ID AS TEXT) AS tenant_name"

_TENANT_TABLE_INFO_SQL = "PRAGMA table_info(tenants)"


def normalize_location(location: str | None) -> str | None:
    """
    Normalize location input across all repositories.
    
    Args:
        location (str, optional): City name, "all", "All Locations", or None
    
    Returns:
        str or None: Normalized city string, or None for "all locations"
    """
    if not location:
        return None

    loc = str(location).strip()
    if not loc or loc.lower() in _ALL_LOCATION_ALIASES:
        return None

    return loc


def _get_tenant_column_names() -> frozenset[str]:
    """
    Load tenant table column names for schema-compatible SQL snippets.
    """
    cols = query_executor.execute_query(_TENANT_TABLE_INFO_SQL, fetch_all=True) or []

    names: set[str] = set()
    for col in cols:
        if isinstance(col, dict):
            name = col.get("name")
            if isinstance(name, str) and name:
                names.add(name)

    return frozenset(names)


def get_tenant_name_select_sql(short: bool = False) -> str:
    """
    Return a SQL snippet selecting a displayable tenant name, compatible with
    both schemas used in this project:
    - tenants(name, ...)
    - tenants(first_name, last_name, ...)
    
    Returns:
        str: SQL snippet for selecting tenant name
    """

    col_names = _get_tenant_column_names()

    if "name" in col_names:
        return _TENANT_NAME_SQL

    if "first_name" in col_names and "last_name" in col_names:
        return _TENANT_SHORT_NAME_SQL if short else _TENANT_FULL_NAME_SQL

    # Fallback: always returns something without referencing unknown columns.
    return _TENANT_FALLBACK_SQL


def parse_date(date_str: str | None) -> date | None:
    """
    Parse a date string into a date object, or return None for blank.
    Uses centralized input_validation module.
    
    Args:
        date_str: Date string to parse (YYYY-MM-DD or DD/MM/YYYY format)
    
    Returns:
        date object or None if invalid/empty
    """
    return input_validation.parse_date(date_str)
