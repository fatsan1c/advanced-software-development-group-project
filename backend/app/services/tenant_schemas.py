"""
Tenant schema layer.

Validates incoming payloads and shapes response payloads for the tenant API.
"""

from __future__ import annotations

from typing import Any

REQUIRED_CREATE_FIELDS = (
    "first_name",
    "last_name",
    "date_of_birth",
    "NI_number",
    "email",
    "phone",
)


def validate_tenant_create_payload(
    payload: dict[str, Any],
) -> tuple[bool, dict[str, str]]:
    """
    Minimal starter validator for tenant create requests.

    Returns:
        (is_valid, errors_dict)
    """
    errors: dict[str, str] = {}

    for field in REQUIRED_CREATE_FIELDS:
        value = payload.get(field)
        if value is None or str(value).strip() == "":
            errors[field] = "This field is required."

    annual_salary = payload.get("annual_salary")
    if annual_salary not in (None, ""):
        try:
            salary_value = float(annual_salary)
            if salary_value < 0:
                errors["annual_salary"] = "Must be >= 0."
        except (TypeError, ValueError):
            errors["annual_salary"] = "Must be a number."

    return (len(errors) == 0, errors)


def tenant_response(row: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize tenant response fields for API output.
    """
    return {
        "tenant_id": row.get("tenant_ID") or row.get("tenant_id"),
        "first_name": row.get("first_name"),
        "last_name": row.get("last_name"),
        "date_of_birth": row.get("date_of_birth"),
        "ni_number": row.get("NI_number") or row.get("ni_number"),
        "email": row.get("email"),
        "phone": row.get("phone"),
        "occupation": row.get("occupation"),
        "annual_salary": row.get("annual_salary"),
        "pets": row.get("pets"),
        "right_to_rent": row.get("right_to_rent"),
        "credit_check": row.get("credit_check"),
    }
