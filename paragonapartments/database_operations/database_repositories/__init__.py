"""Repository package exports.

This module exposes repository classes for explicit instantiation at call sites,
alongside utility helper functions commonly used by UI layers.
"""

from database_operations.database_repositories.apartment_repository import ApartmentsRepository
from database_operations.database_repositories.finance_repository import (
    InvoicesRepository,
    PaymentsRepository,
)
from database_operations.database_repositories.lease_repository import LeaseAgreementsRepository
from database_operations.database_repositories.location_repository import LocationsRepository
from database_operations.database_repositories.maintenance_repository import MaintenanceRequestsRepository
from database_operations.database_repositories.tenant_repository import TenantsRepository
from database_operations.database_repositories.complaint_repository import ComplaintRepository
from database_operations.database_repositories.user_repository import UsersRepository

apartments_repo = ApartmentsRepository()
invoices_repo = InvoicesRepository()
payments_repo = PaymentsRepository()
lease_agreements_repo = LeaseAgreementsRepository()
locations_repo = LocationsRepository()
maintenance_requests_repo = MaintenanceRequestsRepository()
tenants_repo = TenantsRepository()
complaints_repo = ComplaintRepository()
users_repo = UsersRepository()

from database_operations.database_repositories.location_repository import get_location_id_by_city, get_all_cities
from database_operations.database_repositories.tenant_repository import get_all_tenant_names
from database_operations.database_repositories.apartment_repository import get_all_apartments, set_apartment_as_occupied

__all__ = [
    "ApartmentsRepository",
    "LeaseAgreementsRepository",
    "InvoicesRepository",
    "PaymentsRepository",
    "LocationsRepository",
    "MaintenanceRequestsRepository",
    "TenantsRepository",
    "ComplaintRepository",
    "UsersRepository",
    "get_location_id_by_city",
    "get_all_cities",
    "get_all_tenant_names",
    "get_all_apartments",
    "set_apartment_as_occupied"
]