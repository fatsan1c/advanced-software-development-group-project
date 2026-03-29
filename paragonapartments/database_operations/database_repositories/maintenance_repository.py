"""
Maintenance Repository - All maintenance-related database operations.
Handles maintenance requests, scheduling, completion tracking, and cost management.
"""
from __future__ import annotations

from database_operations.database_repositories.base_repository import BaseRepository
from database_operations.db_utils import normalize_location, get_tenant_name_select_sql


class MaintenanceRequestsRepository(BaseRepository):
    """Object-oriented data access for the maintenance_requests table."""

    TABLE = "maintenance_requests"
    ID_FIELD = "request_ID"
    ALLOWED_UPDATE_FIELDS = {
        "issue_description",
        "priority_level",
        "scheduled_date",
        "completed",
        "cost",
    }

    def get_maintenance_requests(
        self,
        location: str | None = None,
        completed: int | None = None,
        priority: int | None = None,
        compact: bool = False,
    ):
        """
        Get maintenance requests enriched with tenant and apartment information.

        Args:
            location (str, optional): City name to filter by, or None/"all" for all locations.
            completed (int, optional): 0 for pending, 1 for completed, None for all.
            priority (int, optional): Priority level (1-5) to filter by, None for all.

        Returns:
            list: List of maintenance request dictionaries.
        """
        city = normalize_location(location)

        apartment_address_sql = "SUBSTR(a.apartment_address, 1, 11) || '...' AS apartment_address" if compact else "a.apartment_address"

        query = f"""
            SELECT
                mr.request_ID,
                mr.apartment_ID,
                mr.tenant_ID,
                {get_tenant_name_select_sql(short=compact)},
                {apartment_address_sql},
                l.city,
                mr.issue_description,
                mr.priority_level,
                mr.reported_date,
                mr.scheduled_date,
                mr.completed,
                mr.cost
            FROM maintenance_requests mr
            JOIN apartments a ON mr.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            JOIN tenants t ON mr.tenant_ID = t.tenant_ID
            WHERE 1=1
        """

        params = []
        if city:
            query += " AND l.city = ?"
            params.append(city)
        if completed in (0, 1):
            query += " AND mr.completed = ?"
            params.append(int(completed))
        if priority is not None:
            query += " AND mr.priority_level = ?"
            params.append(int(priority))

        query += " ORDER BY mr.priority_level DESC, date(mr.reported_date) DESC, mr.request_ID DESC"

        return self._execute(query, tuple(params), fetch_all=True)

    def get_maintenance_request_by_id(self, request_id: int):
        """
        Get a single maintenance request by ID.

        Args:
            request_id (int): The maintenance request ID

        Returns:
            dict: Maintenance request row or None
        """
        query = f"""
            SELECT
                mr.request_ID,
                mr.apartment_ID,
                mr.tenant_ID,
                {get_tenant_name_select_sql()},
                a.apartment_address,
                l.city,
                mr.issue_description,
                mr.priority_level,
                mr.reported_date,
                mr.scheduled_date,
                mr.completed,
                mr.cost
            FROM maintenance_requests mr
            JOIN apartments a ON mr.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            JOIN tenants t ON mr.tenant_ID = t.tenant_ID
            WHERE mr.request_ID = ?
        """
        return self._execute(query, (int(request_id),), fetch_one=True)

    def create_maintenance_request(
        self,
        apartment_id: int,
        tenant_id: int,
        issue_description: str,
        priority_level: int,
        reported_date: str | None = None,
        scheduled_date: str | None = None,
        cost: float | None = None,
    ):
        """
        Create a new maintenance request.

        Args:
            apartment_id (int): Apartment ID
            tenant_id (int): Tenant ID
            issue_description (str): Description of the maintenance issue
            priority_level (int): Priority level (1-5, where 5 is most urgent)
            reported_date (str, optional): Date reported 'YYYY-MM-DD'. Defaults to today.
            scheduled_date (str, optional): Scheduled date 'YYYY-MM-DD'. Can be None.
            cost (float, optional): Estimated or actual cost. Can be None.

        Returns:
            int: New maintenance request ID, or None on failure
        """
        query = """
            INSERT INTO maintenance_requests
            (apartment_ID, tenant_ID, issue_description, priority_level,
             reported_date, scheduled_date, completed, cost)
            VALUES (?, ?, ?, ?, COALESCE(?, date('now')), ?, 0, ?)
        """
        params = (
            int(apartment_id),
            int(tenant_id),
            str(issue_description),
            int(priority_level),
            reported_date,
            scheduled_date,
            float(cost) if cost is not None else None,
        )
        return self._execute(query, params, commit=True)

    def update_maintenance_request(self, request_id: int, **kwargs):
        """
        Update a maintenance request's fields.

        Args:
            request_id (int): The maintenance request ID
            **kwargs: Fields to update (issue_description, priority_level, scheduled_date, cost, completed)

        Returns:
            bool: True if update succeeded, False otherwise
        """
        return self._update_by_id(
            int(request_id),
            kwargs,
            allowed_fields=self.ALLOWED_UPDATE_FIELDS,
        )

    def mark_maintenance_completed(self, request_id: int, cost: float | None = None):
        """
        Mark a maintenance request as completed.

        Args:
            request_id (int): The maintenance request ID
            cost (float, optional): Final cost of the completed work

        Returns:
            bool: True if update succeeded, False otherwise
        """
        updates = {"completed": 1}
        if cost is not None:
            updates["cost"] = float(cost)

        return self._update_by_id(
            int(request_id),
            updates,
            allowed_fields={"completed", "cost"},
        )

    def get_maintenance_stats(self, location: str | None = None):
        """
        Get maintenance statistics for a location or all locations.

        Args:
            location (str, optional): City name to filter by, or None/"all" for all locations.

        Returns:
            dict: Statistics including total, pending, completed, average cost, etc.
        """
        city = normalize_location(location)

        base_where = "WHERE l.city = ?" if city else "WHERE 1=1"
        params = (city,) if city else ()

        query = f"""
            SELECT
                COUNT(*) as total_requests,
                SUM(CASE WHEN mr.completed = 0 THEN 1 ELSE 0 END) as pending_requests,
                SUM(CASE WHEN mr.completed = 1 THEN 1 ELSE 0 END) as completed_requests,
                AVG(CASE WHEN mr.completed = 1 AND mr.cost IS NOT NULL THEN mr.cost END) as avg_cost,
                SUM(CASE WHEN mr.priority_level >= 4 AND mr.completed = 0 THEN 1 ELSE 0 END) as high_priority_pending
            FROM maintenance_requests mr
            JOIN apartments a ON mr.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            {base_where}
        """

        return self._execute(query, params, fetch_one=True)

    def get_scheduled_maintenance(self, location: str | None = None, date_from: str | None = None):
        """
        Get scheduled maintenance requests within a date range.

        Args:
            location (str, optional): City name to filter by, or None/"all" for all locations.
            date_from (str, optional): Start date 'YYYY-MM-DD'. Defaults to today.
            date_to (str, optional): End date 'YYYY-MM-DD'. Defaults to 30 days from today.

        Returns:
            list: List of scheduled maintenance request dictionaries.
        """
        city = normalize_location(location)

        query = f"""
            SELECT
                mr.request_ID,
                mr.apartment_ID,
                mr.tenant_ID,
                {get_tenant_name_select_sql()},
                a.apartment_address,
                l.city,
                mr.issue_description,
                mr.priority_level,
                mr.reported_date,
                mr.scheduled_date,
                mr.completed,
                mr.cost
            FROM maintenance_requests mr
            JOIN apartments a ON mr.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            JOIN tenants t ON mr.tenant_ID = t.tenant_ID
            WHERE mr.scheduled_date IS NOT NULL
              AND mr.completed = 0
              AND date(mr.scheduled_date) >= COALESCE(date(?), date('now'))
        """

        params = [date_from]
        if city:
            query += " AND l.city = ?"
            params.append(city)

        query += " ORDER BY date(mr.scheduled_date) ASC, mr.priority_level DESC"

        return self._execute(query, tuple(params), fetch_all=True)

    def delete_maintenance_request(self, request_id: int):
        """
        Delete a maintenance request.

        Args:
            request_id (int): The maintenance request ID

        Returns:
            bool: True if deletion succeeded, False otherwise
        """
        return self._delete_by_id(int(request_id))

    def get_apartments_with_tenants(self, location: str | None = None):
        """
        Get apartments with active leases including tenant information.

        Args:
            location (str, optional): City name to filter by, or None/"all" for all locations.

        Returns:
            list: List of apartment dictionaries with tenant info.
        """
        city = normalize_location(location)

        query = f"""
            SELECT
                a.apartment_ID,
                a.apartment_address,
                la.tenant_ID,
                {get_tenant_name_select_sql()},
                l.city
            FROM apartments a
            JOIN lease_agreements la ON a.apartment_ID = la.apartment_ID
            JOIN tenants t ON la.tenant_ID = t.tenant_ID
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE la.active = 1
        """

        params = []
        if city:
            query += " AND l.city = ?"
            params.append(city)

        query += " ORDER BY l.city, a.apartment_address"

        return self._execute(query, tuple(params), fetch_all=True)

