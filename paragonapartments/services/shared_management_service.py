"""Contributors: Aaron Antal-Bento (23013693), Ollie Churchley (23020494)

Shared CRUD helpers for administrator and manager services."""

from __future__ import annotations

import sqlite3

from database_operations.database_repositories import apartments_repo, locations_repo, users_repo


def resolve_location_id(location: str | None) -> int | None:
    """Resolve a city name to a location ID, treating empty/None as no location."""
    if not location or location == "None":
        return None
    return locations_repo.get_location_id_by_city(location)


def to_occupied_flag(status: str | int | None) -> int:
    """Normalize apartment occupied status to repository integer flag."""
    if isinstance(status, str):
        normalized = status.strip().lower()
        if normalized in {"occupied", "1", "true", "yes", "y"}:
            return 1
        if normalized in {"vacant", "0", "false", "no", "n"}:
            return 0
        raise ValueError(f"Unknown occupancy status: {status}")
    return int(status or 0)


def create_account(username: str, role: str, password: str, location: str | None):
    """Create a user account with optional location binding."""
    try:
        location_id = resolve_location_id(location)
        users_repo.create_user(username, password, role, location_id)
        return True
    except (ValueError, TypeError) as e:
        return f"Invalid account input: {str(e)}"
    except sqlite3.Error as e:
        return f"Failed to create account: {str(e)}"


def edit_account(user_data, username: str, role: str, location: str | None):
    """Edit user account fields with optional location binding."""
    try:
        user_id = user_data.get("user_ID") if user_data else None
        if user_id is None:
            return "No valid user identifier provided."

        location_id = resolve_location_id(location)
        users_repo.update_user(int(user_id), username=username, role=role, location_ID=location_id)
        return True
    except (ValueError, TypeError) as e:
        return f"Invalid account input: {str(e)}"
    except sqlite3.Error as e:
        return f"Failed to edit account: {str(e)}"


def delete_account(user_data):
    """Delete a user account by user_ID key in the provided payload."""
    try:
        if user_data and "user_ID" in user_data:
            users_repo.delete_user(int(user_data["user_ID"]))
            return True
        return "No valid user identifier provided."
    except (ValueError, TypeError) as e:
        return f"Invalid user identifier: {str(e)}"
    except sqlite3.Error as e:
        return f"Failed to delete account: {str(e)}"


def add_apartment(location: str | None, apartment_data):
    """Create an apartment record for the given location and payload."""
    apartment_address = apartment_data.get("Apartment Address", "")
    number_of_beds = apartment_data.get("Number of Beds", 0)
    monthly_rent = apartment_data.get("Monthly Rent", 0)
    status = apartment_data.get("Status", "Vacant")

    try:
        location_id = resolve_location_id(location)
        if location_id is None:
            return "Invalid location specified."

        apartments_repo.create_apartment(
            location_id,
            apartment_address,
            number_of_beds,
            monthly_rent,
            to_occupied_flag(status),
        )
        return True
    except (ValueError, TypeError) as e:
        return f"Invalid apartment input: {str(e)}"
    except sqlite3.Error as e:
        return f"Failed to add apartment: {str(e)}"


def delete_apartment(apartment_data):
    """Delete an apartment by apartment_ID key in the provided payload."""
    try:
        if apartment_data and "apartment_ID" in apartment_data:
            apartments_repo.delete_apartment(int(apartment_data["apartment_ID"]))
            return True
        return "No valid apartment identifier provided."
    except (ValueError, TypeError) as e:
        return f"Invalid apartment identifier: {str(e)}"
    except sqlite3.Error as e:
        return f"Failed to delete apartment: {str(e)}"


def edit_apartment(location: str | None, apartment_data, values):
    """Edit apartment fields for the given location and row payload."""
    try:
        apartment_id = apartment_data.get("apartment_ID") if apartment_data else None
        if apartment_id is None:
            return "No valid apartment identifier provided."

        location_id = resolve_location_id(location)
        if location_id is None:
            return "Invalid location specified."

        apartments_repo.update_apartment(
            int(apartment_id),
            location_ID=location_id,
            apartment_address=values.get("apartment_address", ""),
            number_of_beds=values.get("number_of_beds", 0),
            monthly_rent=values.get("monthly_rent", 0),
            occupied=to_occupied_flag(values.get("occupied", 0)),
        )
        return True
    except (ValueError, TypeError) as e:
        return f"Invalid apartment input: {str(e)}"
    except sqlite3.Error as e:
        return f"Failed to edit apartment: {str(e)}"
