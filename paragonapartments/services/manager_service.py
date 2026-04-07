"""Manager business operations extracted from UI-facing role classes."""

from __future__ import annotations

from database_operations.database_repositories import (
    apartments_repo,
    lease_agreements_repo,
    locations_repo,
    users_repo,
)
from . import shared_management_service as shared_mgmt


class ManagerService:
    """Domain/service layer for manager account, location, and apartment operations."""

    @staticmethod
    def view_apartment_occupancy(location: str):
        """View apartment occupancy for a specific location or all locations."""
        try:
            return apartments_repo.get_all_occupancy(location)
        except Exception:
            return 0

    @staticmethod
    def get_total_apartments(location: str):
        """Return apartment unit count for a specific location or all locations."""
        return apartments_repo.get_total_apartments(location)

    @staticmethod
    def get_monthly_revenue(location: str):
        """Return current monthly revenue for a specific location or all locations."""
        return apartments_repo.get_monthly_revenue(location)

    @staticmethod
    def get_potential_revenue(location: str):
        """Return potential monthly revenue for a specific location or all locations."""
        return apartments_repo.get_potential_revenue(location)

    @staticmethod
    def get_lease_date_range(location: str, grouping: str = "month"):
        """Return lease date range for manager dashboard graphs."""
        return lease_agreements_repo.get_lease_date_range(location, grouping=grouping)

    @staticmethod
    def get_all_users():
        """Return all users for manager account management views."""
        return users_repo.get_all_users()

    @staticmethod
    def get_all_cities():
        """Return all city names for manager filters and dropdowns."""
        return locations_repo.get_all_cities()

    @staticmethod
    def get_all_locations():
        """Return all location rows for manager location management views."""
        return locations_repo.get_all_locations()

    @staticmethod
    def get_all_apartments(location: str = "all"):
        """Return apartments for a location or all locations."""
        return apartments_repo.get_all_apartments(location=location)

    @staticmethod
    def create_account(values):
        """Create a new user account with specified role and location."""
        return shared_mgmt.create_account(
            username=values.get("Username", ""),
            role=values.get("Role", ""),
            password=values.get("Password", ""),
            location=values.get("Location", None),
        )

    @staticmethod
    def edit_account(user_data, values):
        """Edit an existing user account's role and location."""
        return shared_mgmt.edit_account(
            user_data=user_data,
            username=values.get("username", ""),
            role=values.get("role", ""),
            location=values.get("city", None),
        )

    @staticmethod
    def delete_account(user_data):
        """Delete an existing user account by username or ID."""
        return shared_mgmt.delete_account(user_data)

    @staticmethod
    def expand_business(new_location: dict[str, str]):
        """Expand business to a new location."""
        city = new_location.get("City", "")
        address = new_location.get("Address", "")

        if not city.strip():
            return "City is required."
        if not address.strip():
            return "Address is required."

        try:
            locations_repo.create_location(city, address)
            return True
        except Exception as e:
            return f"Failed to add location: {str(e)}"

    @staticmethod
    def edit_location(location_data, values):
        """Edit an existing location's city and address."""
        location_id = location_data.get("location_ID", None)
        city = values.get("city", "")
        address = values.get("address", "")

        try:
            locations_repo.update_location(int(location_id), city=city, address=address)
            return True
        except Exception as e:
            return f"Failed to edit location: {str(e)}"

    @staticmethod
    def delete_location(location_data):
        """Delete an existing location by ID."""
        try:
            if location_data and "location_ID" in location_data:
                locations_repo.delete_location(int(location_data["location_ID"]))
            else:
                return "No valid location identifier provided."

            return True
        except Exception as e:
            return f"Failed to delete location: {str(e)}"

    @staticmethod
    def add_apartment(apartment_data):
        """Add a new apartment to the system."""
        return shared_mgmt.add_apartment(apartment_data.get("Location", ""), apartment_data)

    @staticmethod
    def delete_apartment(apartment_data):
        """Delete an existing apartment by ID."""
        return shared_mgmt.delete_apartment(apartment_data)

    @staticmethod
    def edit_apartment(apartment_data, values):
        """Edit an existing apartment's details."""
        return shared_mgmt.edit_apartment(values.get("city", ""), apartment_data, values)
