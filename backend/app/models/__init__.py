"""
Backend domain models (SQLAlchemy).

These map 1:1 to the existing SQLite schema used by the desktop app.
"""

from .location import Location
from .apartment import Apartment
from .tenant import Tenant
from .lease_agreement import LeaseAgreement
from .user import User
from .invoice import Invoice
from .payment import Payment
from .complaint import Complaint
from .maintenance_request import MaintenanceRequest

__all__ = [
    "Location",
    "Apartment",
    "Tenant",
    "LeaseAgreement",
    "User",
    "Invoice",
    "Payment",
    "Complaint",
    "MaintenanceRequest",
]

