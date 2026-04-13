"""Contributors: Oliver Mercer (24026901), Nickolas Greiner (24018357)"""
from __future__ import annotations

from database_operations.database_repositories.base_repository import BaseRepository
from database_operations.database_repositories.location_repository import get_location_id_by_city


class TenantsRepository(BaseRepository):
    """Object-oriented data access for tenant-centric operations."""

    TABLE = "tenants"
    ID_FIELD = "tenant_ID"
    ALLOWED_UPDATE_FIELDS = {
        "first_name",
        "last_name",
        "date_of_birth",
        "NI_number",
        "email",
        "phone",
        "occupation",
        "annual_salary",
        "pets",
        "right_to_rent",
        "credit_check",
    }

    def create_tenant(self, first_name, last_name, date_of_birth, NI_number, email, phone, occupation=None, annual_salary=None, pets="N", right_to_rent="N", credit_check="Pending"):
        """Create a new tenant in the database."""
        return self._insert(
            {
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": date_of_birth,
                "NI_number": NI_number,
                "email": email,
                "phone": phone,
                "occupation": occupation,
                "annual_salary": annual_salary,
                "pets": pets,
                "right_to_rent": right_to_rent,
                "credit_check": credit_check,
            },
        )

    def get_all_tenant_names(self):
        """Retrieve all tenant names from the database."""
        return self._get_all(
            columns=["first_name", "last_name", "tenant_ID"],
            order_by="tenant_ID",
        )

    def update_tenant(self, tenant_id, **kwargs):
        """Update tenant information in the database."""
        return self._update_by_id(
            tenant_id,
            kwargs,
            allowed_fields=self.ALLOWED_UPDATE_FIELDS,
        )

    def get_last_tenant_id(self):
        """Get the ID of the most recently created tenant."""
        query = "SELECT MAX(tenant_ID) as last_id FROM tenants"
        result = self._execute(query, fetch_one=True)
        return result["last_id"] if result and result["last_id"] else None

    def get_tenant_by_id(self, tenant_id, location=None):
        """Retrieve a tenant's information by their ID, optionally filtered by location."""
        if location:
            location_id = get_location_id_by_city(location)
            if not location_id:
                return None

            query = """
            SELECT DISTINCT t.*
            FROM tenants t
            INNER JOIN lease_agreements la ON t.tenant_ID = la.tenant_ID
            INNER JOIN apartments a ON la.apartment_ID = a.apartment_ID
            WHERE t.tenant_ID = ? AND a.location_ID = ?
            """
            return self._execute(query, (tenant_id, location_id), fetch_one=True)

        return self._get_by_id(tenant_id)

    def get_all_tenants(self, location=None):
        """Retrieve all tenants from the database, optionally filtered by location."""
        if location:
            location_id = get_location_id_by_city(location)
            if not location_id:
                return []

            query = """
            SELECT t.*
            FROM tenants t
            WHERE t.tenant_ID IN (
                SELECT DISTINCT la.tenant_ID
                FROM lease_agreements la
                INNER JOIN apartments a ON la.apartment_ID = a.apartment_ID
                WHERE a.location_ID = ?
            )
            ORDER BY t.first_name, t.last_name
            """
            return self._execute(query, (location_id,), fetch_all=True)

        return self._get_all(order_by="first_name, last_name")

    def search_tenants(self, search_term, location=None):
        """Search for tenants by name, email, NI number, or phone, optionally filtered by location."""
        search_pattern = f"%{search_term}%"

        if location:
            location_id = get_location_id_by_city(location)
            if not location_id:
                return []

            query = """
            SELECT t.*
            FROM tenants t
            WHERE (t.first_name LIKE ? OR t.last_name LIKE ? OR t.email LIKE ? OR t.NI_number LIKE ? OR t.phone LIKE ?)
            AND t.tenant_ID IN (
                SELECT DISTINCT la.tenant_ID
                FROM lease_agreements la
                INNER JOIN apartments a ON la.apartment_ID = a.apartment_ID
                WHERE a.location_ID = ?
            )
            ORDER BY t.first_name, t.last_name
            """
            return self._execute(
                query,
                (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, location_id),
                fetch_all=True,
            )

        query = """
        SELECT * FROM tenants
        WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR NI_number LIKE ? OR phone LIKE ?
        ORDER BY first_name, last_name
        """
        return self._execute(
            query,
            (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern),
            fetch_all=True,
        )

def get_all_tenant_names():
    """Utility function to get all tenant names."""
    return TenantsRepository().get_all_tenant_names()
