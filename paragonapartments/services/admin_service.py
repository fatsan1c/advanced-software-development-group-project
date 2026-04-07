"""Administrator business operations extracted from UI-facing role classes."""

from __future__ import annotations

from database_operations.database_repositories import (
    apartments_repo,
    lease_agreements_repo,
    locations_repo,
    users_repo,
)
from . import shared_management_service as shared_mgmt


class AdminService:
    """Domain/service layer for administrator account and apartment operations."""

    @staticmethod
    def view_apartment_occupancy(location: str):
        """View apartment occupancy for an administrator location."""
        try:
            return apartments_repo.get_all_occupancy(location)
        except Exception:
            return 0

    @staticmethod
    def get_total_apartments(location: str):
        """Return apartment unit count for an administrator location."""
        return apartments_repo.get_total_apartments(location)

    @staticmethod
    def get_monthly_revenue(location: str):
        """Return current monthly revenue for an administrator location."""
        return apartments_repo.get_monthly_revenue(location)

    @staticmethod
    def get_potential_revenue(location: str):
        """Return potential monthly revenue for an administrator location."""
        return apartments_repo.get_potential_revenue(location)

    @staticmethod
    def get_lease_date_range(location: str, grouping: str = "month"):
        """Return lease date range for admin dashboard graphs."""
        return lease_agreements_repo.get_lease_date_range(location, grouping=grouping)

    @staticmethod
    def get_lease_statistics(location: str):
        """Return lease summary statistics for an administrator location."""
        return lease_agreements_repo.get_lease_statistics(location)

    @staticmethod
    def get_all_leases(location: str):
        """Return all leases for an administrator location."""
        return lease_agreements_repo.get_all_leases(location=location)

    @staticmethod
    def get_all_users(location: str):
        """Return users scoped to the administrator location."""
        all_users = users_repo.get_all_users()
        return [user for user in all_users if user.get("city") == location]

    @staticmethod
    def get_all_cities():
        """Return all city names for admin location selector usage."""
        return locations_repo.get_all_cities()

    @staticmethod
    def get_all_apartments(location: str):
        """Return apartments scoped to the administrator location."""
        return apartments_repo.get_all_apartments(location=location)

    @staticmethod
    def create_account(location: str, values):
        """Create a new user account at the specified administrator location."""
        return shared_mgmt.create_account(
            username=values.get("Username", ""),
            role=values.get("Role", ""),
            password=values.get("Password", ""),
            location=location,
        )

    @staticmethod
    def edit_account(location: str, user_data, values):
        """Edit an existing user account at administrator location."""
        return shared_mgmt.edit_account(
            user_data=user_data,
            username=values.get("username", ""),
            role=values.get("role", ""),
            location=location,
        )

    @staticmethod
    def delete_account(user_data):
        """Delete an existing user account by ID."""
        return shared_mgmt.delete_account(user_data)

    @staticmethod
    def add_apartment(location: str, apartment_data):
        """Add a new apartment at administrator location."""
        return shared_mgmt.add_apartment(location, apartment_data)

    @staticmethod
    def delete_apartment(apartment_data):
        """Delete an existing apartment by ID."""
        return shared_mgmt.delete_apartment(apartment_data)

    @staticmethod
    def edit_apartment(location: str, apartment_data, values):
        """Edit apartment details at administrator location."""
        return shared_mgmt.edit_apartment(location, apartment_data, values)
