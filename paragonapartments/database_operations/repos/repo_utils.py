"""
Repository Utilities - Shared utility functions for repository modules.
"""

from database_operations.db_execute import execute_query
import pages.components.input_validation as input_validation
from datetime import date as _date


# Global cache for tenant name SQL snippet
_TENANT_NAME_SELECT_SQL: str | None = None


def normalize_location(location):
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
    if not loc or loc.lower() in {"all", "all locations", "alllocation", "alllocations"}:
        return None
    return loc


def get_tenant_name_select_sql() -> str:
    """
    Return a SQL snippet selecting a displayable tenant name, compatible with
    both schemas used in this project:
    - tenants(name, ...)
    - tenants(first_name, last_name, ...)
    
    This function caches the result after first execution for performance.
    
    Returns:
        str: SQL snippet for selecting tenant name
    """
    global _TENANT_NAME_SELECT_SQL
    if _TENANT_NAME_SELECT_SQL is not None:
        return _TENANT_NAME_SELECT_SQL

    cols = execute_query("PRAGMA table_info(tenants)", fetch_all=True) or []
    col_names = {c.get("name") for c in cols}

    if "name" in col_names:
        _TENANT_NAME_SELECT_SQL = "t.name AS tenant_name"
    elif "first_name" in col_names and "last_name" in col_names:
        _TENANT_NAME_SELECT_SQL = "(t.first_name || ' ' || t.last_name) AS tenant_name"
    else:
        # Fallback: always returns something without referencing unknown columns
        _TENANT_NAME_SELECT_SQL = "CAST(t.tenant_ID AS TEXT) AS tenant_name"

    return _TENANT_NAME_SELECT_SQL


def parse_date(date_str: str | None, strict: bool = False) -> _date | None:
    """
    Parse a date string into a date object, or return None for blank.
    Uses centralized input_validation module.
    
    Args:
        date_str: Date string to parse (YYYY-MM-DD or DD/MM/YYYY format)
        strict: If True, raises ValueError on invalid date. If False, returns None.
    
    Returns:
        date object or None if invalid/empty
        
    Raises:
        ValueError: If strict=True and date is provided but invalid
    """
    if date_str is None:
        return None
    s = str(date_str).strip()
    if not s:
        return None
    
    # Use centralized validation
    parsed = input_validation.parse_date(s)
    
    if parsed is None and strict:
        raise ValueError(f"Invalid date '{date_str}'. Expected YYYY-MM-DD or DD/MM/YYYY.")
    
    return parsed
