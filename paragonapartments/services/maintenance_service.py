"""Contributors: Ollie Churchley (23020494)

Maintenance business operations extracted from UI-facing role classes."""

from __future__ import annotations

from database_operations.database_repositories import (
    get_all_cities as repo_get_all_cities,
    maintenance_requests_repo,
)


class MaintenanceService:
    """Domain/service layer for maintenance request workflows."""

    @staticmethod
    def get_maintenance_stats(location: str = "all"):
        """Return maintenance statistics for a location scope."""
        return maintenance_requests_repo.get_maintenance_stats(location)

    @staticmethod
    def get_all_cities():
        """Return all city names for maintenance location filters."""
        return repo_get_all_cities()

    @staticmethod
    def get_maintenance_requests(
        location: str = "all",
        completed: int | None = None,
        priority: int | None = None,
        compact: bool = False,
    ):
        """Return maintenance requests for a location with optional filters."""
        return maintenance_requests_repo.get_maintenance_requests(
            location=location,
            completed=completed,
            priority=priority,
            compact=compact,
        )

    @staticmethod
    def update_maintenance_request(request_id: int, **kwargs):
        """Update maintenance request fields by ID."""
        return maintenance_requests_repo.update_maintenance_request(request_id, **kwargs)

    @staticmethod
    def delete_maintenance_request(request_id: int):
        """Delete maintenance request by ID."""
        return maintenance_requests_repo.delete_maintenance_request(request_id)

    @staticmethod
    def get_apartments_with_tenants(location: str = "all"):
        """Return apartments with active tenants for maintenance request creation."""
        return maintenance_requests_repo.get_apartments_with_tenants(location)

    @staticmethod
    def get_scheduled_maintenance(location: str = "all"):
        """Return scheduled maintenance items for a location."""
        return maintenance_requests_repo.get_scheduled_maintenance(location)

    @staticmethod
    def create_maintenance_request(values):
        """Create a new maintenance request."""
        try:
            apartment_id = int(values.get("Apartment ID", 0))
            tenant_id = int(values.get("Tenant ID", 0))
            issue_description = values.get("Issue Description", "").strip()
            priority_level = int(values.get("Priority Level", 1))
            scheduled_date = values.get("Scheduled Date", "").strip() or None
            cost_estimate = values.get("Cost Estimate", "").strip()

            if not apartment_id:
                return "Apartment ID is required."
            if not tenant_id:
                return "Tenant ID is required."
            if not issue_description:
                return "Issue Description is required."
            if priority_level < 1 or priority_level > 5:
                return "Priority Level must be between 1 (low) and 5 (urgent)."

            cost = float(cost_estimate) if cost_estimate else None

            request_id = maintenance_requests_repo.create_maintenance_request(
                apartment_id=apartment_id,
                tenant_id=tenant_id,
                issue_description=issue_description,
                priority_level=priority_level,
                scheduled_date=scheduled_date,
                cost=cost,
            )
            return True if request_id else "Failed to create maintenance request."
        except Exception as e:
            return f"Failed to create request: {str(e)}"

    @staticmethod
    def update_maintenance_request_row(row_data, updated_data):
        """Update a maintenance request row from editable table data."""
        try:
            request_id = int(row_data.get("request_ID"))
            kwargs = {}

            if "priority_level" in updated_data:
                priority = int(updated_data["priority_level"])
                if priority < 1 or priority > 5:
                    return "Priority must be between 1 and 5."
                kwargs["priority_level"] = priority

            if "issue_description" in updated_data:
                kwargs["issue_description"] = updated_data["issue_description"]

            if "scheduled_date" in updated_data:
                kwargs["scheduled_date"] = updated_data["scheduled_date"] or None

            if "cost" in updated_data:
                cost_str = str(updated_data["cost"]).strip()
                kwargs["cost"] = float(cost_str) if cost_str else None

            if "completed" in updated_data:
                kwargs["completed"] = int(updated_data["completed"])

            success = maintenance_requests_repo.update_maintenance_request(request_id, **kwargs)
            return True if success else "Update failed."
        except Exception as e:
            return f"Failed to update request: {str(e)}"

    @staticmethod
    def delete_maintenance_request_row(row_data):
        """Delete a maintenance request row from the table."""
        try:
            request_id = int(row_data.get("request_ID"))
            success = maintenance_requests_repo.delete_maintenance_request(request_id)
            return True if success else "Delete failed."
        except Exception as e:
            return f"Failed to delete request: {str(e)}"

    @staticmethod
    def complete_maintenance_request(values):
        """Mark a maintenance request as completed and log final cost."""
        try:
            request_id = int(values.get("Request ID", 0))
            final_cost = values.get("Final Cost", "").strip()

            if not request_id:
                return "Request ID is required."

            request = maintenance_requests_repo.get_maintenance_request_by_id(request_id)
            if not request:
                return f"Maintenance request ID {request_id} does not exist."
            if int(request.get("completed", 0)) == 1:
                return f"Request {request_id} is already marked as completed."

            cost = float(final_cost) if final_cost else None
            success = maintenance_requests_repo.mark_maintenance_completed(request_id, cost)

            return True if success else "Failed to mark request as completed."
        except Exception as e:
            return f"Failed to complete request: {str(e)}"

    @staticmethod
    def schedule_maintenance(values):
        """Schedule a maintenance request by updating the scheduled date."""
        try:
            request_id = int(values.get("Request ID", 0))
            scheduled_date = values.get("Scheduled Date", "").strip()

            if not request_id:
                return "Request ID is required."
            if not scheduled_date:
                return "Scheduled Date is required (YYYY-MM-DD)."

            request = maintenance_requests_repo.get_maintenance_request_by_id(request_id)
            if not request:
                return f"Maintenance request ID {request_id} does not exist."
            if int(request.get("completed", 0)) == 1:
                return f"Cannot schedule completed request {request_id}."

            success = maintenance_requests_repo.update_maintenance_request(
                request_id,
                scheduled_date=scheduled_date,
            )

            return True if success else "Failed to schedule request."
        except Exception as e:
            return f"Failed to schedule request: {str(e)}"
