"""
Contributors: Oliver Mercer (24026901), Nickolas Greiner (24018357)

Complaint repository for complaint-specific database operations."""

from __future__ import annotations

from database_operations.database_repositories.base_repository import BaseRepository
from database_operations.database_repositories.location_repository import get_location_id_by_city


class ComplaintRepository(BaseRepository):
    """Object-oriented data access for the complaint table."""

    TABLE = "complaint"
    ID_FIELD = "complaint_ID"

    def create_complaint(self, tenant_id, description, date_submitted):
        """Create a new complaint."""
        return self._insert(
            {
                "tenant_ID": tenant_id,
                "description": description,
                "date_submitted": date_submitted,
                "resolved": 0,
            },
        )

    def get_complaints_by_tenant(self, tenant_id):
        """Get all complaints for a specific tenant."""
        return self._get_all_by_field("tenant_ID", tenant_id, order_by="date_submitted DESC")

    def get_all_complaints(self, location=None):
        """Get all complaints, optionally filtered by location."""
        if location:
            location_id = get_location_id_by_city(location)
            if not location_id:
                return []

            query = """
            SELECT c.*,
                   (t.first_name || ' ' || t.last_name) as tenant_name
            FROM complaint c
            LEFT JOIN tenants t ON c.tenant_ID = t.tenant_ID
            LEFT JOIN lease_agreements la ON t.tenant_ID = la.tenant_ID
            LEFT JOIN apartments a ON la.apartment_ID = a.apartment_ID
            WHERE a.location_ID = ?
            GROUP BY c.complaint_ID
            ORDER BY c.resolved, c.date_submitted DESC
            """
            return self._execute(query, (location_id,), fetch_all=True)

        query = """
        SELECT c.*,
               (t.first_name || ' ' || t.last_name) as tenant_name
        FROM complaint c
        LEFT JOIN tenants t ON c.tenant_ID = t.tenant_ID
        ORDER BY c.resolved, c.date_submitted DESC
        """
        return self._execute(query, fetch_all=True)

    def delete_complaint(self, complaint_id):
        """Delete a complaint by ID."""
        return self._delete_by_id(complaint_id)

    def update_complaint_status(self, complaint_id, resolved):
        """Update the resolved status of a complaint."""
        return self._update_by_id(
            complaint_id,
            {"resolved": resolved},
            allowed_fields={"resolved"},
        )