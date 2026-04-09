"""Contributors: Oliver Mercer (24026901), Nickolas Greiner (24018357)

Front desk business operations extracted from UI-facing role classes."""

from __future__ import annotations

from database_operations.database_repositories import (
    complaints_repo,
    get_all_apartments as repo_get_all_apartments,
    get_all_cities as repo_get_all_cities,
    lease_agreements_repo,
    maintenance_requests_repo,
    set_apartment_as_occupied,
    tenants_repo,
)


class FrontDeskService:
    """Domain/service layer for front desk tenant and request workflows."""

    @staticmethod
    def register_tenant(values):
        """Register a tenant and create corresponding lease + occupancy updates."""
        first_name = values.get("First Name", "")
        last_name = values.get("Last Name", "")
        date_of_birth = values.get("Date of Birth", "")
        ni_number = values.get("NI Number", "")
        email = values.get("Email", "")
        phone = values.get("Phone", "")
        occupation = values.get("Occupation", "")
        annual_salary = values.get("Annual Salary", "")
        pets = values.get("Pets", "N")
        right_to_rent = values.get("Right to Rent", "N")
        credit_check = values.get("Credit Check", "Pending")

        city = values.get("City", "")
        apartment_full = values.get("Apartment", "")
        apartment = apartment_full.split(" - ")[0] if " - " in apartment_full else apartment_full
        start_date = values.get("Contract Start Date", "")
        end_date = values.get("Contract End Date", "")

        try:
            salary_value = float(annual_salary) if annual_salary and annual_salary.strip() else None

            tenants_repo.create_tenant(
                first_name,
                last_name,
                date_of_birth,
                ni_number,
                email,
                phone,
                occupation,
                salary_value,
                pets,
                right_to_rent,
                credit_check,
            )

            tenant_id = tenants_repo.get_last_tenant_id()

            if tenant_id and apartment:
                all_apartments = repo_get_all_apartments()
                apartment_id = None
                monthly_rent = 0

                for apt in all_apartments:
                    if apt["apartment_address"] == apartment and apt["city"] == city:
                        apartment_id = apt["apartment_ID"]
                        monthly_rent = apt["monthly_rent"]
                        break

                if apartment_id:
                    lease_agreements_repo.create_lease_agreement(
                        tenant_id,
                        apartment_id,
                        start_date,
                        end_date,
                        monthly_rent,
                    )
                    set_apartment_as_occupied(apartment_id)

            return True
        except Exception as e:
            return f"Failed to register tenant: {str(e)}"

    @staticmethod
    def get_tenant_info(location: str, tenant_id: int | None = None):
        """Retrieve formatted tenant information for the specified location."""
        result = tenants_repo.get_tenant_by_id(tenant_id, location=location) if tenant_id else None
        if result:
            info = (
                f"Tenant ID: {result['tenant_ID']}\n"
                f"Name: {result['first_name']} {result['last_name']}\n"
                f"Date of Birth: {result.get('date_of_birth', 'N/A')}\n"
                f"NI Number: {result['NI_number']}\n"
                f"Email: {result['email']}\n"
                f"Phone: {result['phone']}\n"
                f"Occupation: {result.get('occupation', 'N/A')}\n"
                f"Annual Salary: £{result.get('annual_salary', 'N/A') if result.get('annual_salary') else 'N/A'}\n"
                f"Pets: {result.get('pets', 'N/A')}\n"
                f"Right to Rent: {result.get('right_to_rent', 'N/A')}\n"
                f"Credit Check: {result.get('credit_check', 'N/A')}"
            )
            return info
        return "Tenant not found or not in your location"

    @staticmethod
    def update_tenant(tenant_id, values):
        """Update existing tenant fields."""
        try:
            update_fields = {}

            if values.get("First Name"):
                update_fields["first_name"] = values["First Name"]
            if values.get("Last Name"):
                update_fields["last_name"] = values["Last Name"]
            if values.get("Date of Birth"):
                update_fields["date_of_birth"] = values["Date of Birth"]
            if values.get("NI Number"):
                update_fields["NI_number"] = values["NI Number"]
            if values.get("Email"):
                update_fields["email"] = values["Email"]
            if values.get("Phone"):
                update_fields["phone"] = values["Phone"]
            if values.get("Occupation"):
                update_fields["occupation"] = values["Occupation"]
            if values.get("Annual Salary"):
                update_fields["annual_salary"] = float(values["Annual Salary"]) if values["Annual Salary"].strip() else None
            if values.get("Pets"):
                update_fields["pets"] = values["Pets"]
            if values.get("Right to Rent"):
                update_fields["right_to_rent"] = values["Right to Rent"]
            if values.get("Credit Check"):
                update_fields["credit_check"] = values["Credit Check"]

            tenants_repo.update_tenant(tenant_id, **update_fields)
            return True
        except Exception as e:
            return f"Failed to update tenant: {str(e)}"

    @staticmethod
    def register_maintenance_request(values):
        """Register a maintenance request for a tenant."""
        try:
            apartment_id = values.get("apartment_id")
            tenant_id = values.get("tenant_id")
            issue_description = values.get("issue_description")
            priority_level = values.get("priority_level", 2)
            reported_date = values.get("reported_date")

            maintenance_requests_repo.create_maintenance_request(
                apartment_id,
                tenant_id,
                issue_description,
                priority_level,
                reported_date,
            )
            return True
        except Exception as e:
            return f"Failed to register maintenance request: {str(e)}"

    @staticmethod
    def register_complaint(values):
        """Register a complaint from a tenant."""
        try:
            tenant_id = values.get("tenant_id")
            description = values.get("description")
            date_submitted = values.get("date_submitted")

            complaints_repo.create_complaint(tenant_id, description, date_submitted)
            return True
        except Exception as e:
            return f"Failed to register complaint: {str(e)}"

    @staticmethod
    def get_all_apartments(location: str = "all"):
        """Return apartments for all locations or a specific location."""
        return repo_get_all_apartments(location)

    @staticmethod
    def get_tenant_by_id(location: str, tenant_id: int):
        """Return a tenant by ID scoped to front desk location."""
        return tenants_repo.get_tenant_by_id(tenant_id, location=location)

    @staticmethod
    def search_tenants(location: str, search_term: str):
        """Search tenants scoped to front desk location."""
        return tenants_repo.search_tenants(search_term, location=location)

    @staticmethod
    def get_all_tenants(location: str):
        """Return all tenants scoped to front desk location."""
        return tenants_repo.get_all_tenants(location=location)

    @staticmethod
    def get_all_complaints(location: str):
        """Return all complaints scoped to front desk location."""
        return complaints_repo.get_all_complaints(location=location)

    @staticmethod
    def update_complaint_status(complaint_id: int, resolved: int):
        """Update complaint status."""
        return complaints_repo.update_complaint_status(complaint_id, resolved)

    @staticmethod
    def delete_complaint(complaint_id: int):
        """Delete a complaint by ID."""
        return complaints_repo.delete_complaint(complaint_id)

    @staticmethod
    def get_all_cities():
        """Return all city names for location dropdowns."""
        return repo_get_all_cities()

    @staticmethod
    def get_maintenance_requests(
        location: str,
        completed: int | None = None,
        priority: int | None = None,
        compact: bool = False,
    ):
        """Return maintenance requests scoped to location with optional filters."""
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
