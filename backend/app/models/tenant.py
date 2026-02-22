from __future__ import annotations

from ..extensions import db


class Tenant(db.Model):
    __tablename__ = "tenants"

    tenant_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.String, nullable=False)
    NI_number = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String, nullable=False)
    occupation = db.Column(db.String)
    annual_salary = db.Column(db.Float)
    pets = db.Column(db.String, default="N")
    right_to_rent = db.Column(db.String, default="N")
    credit_check = db.Column(db.String, default="Pending")

    lease_agreements = db.relationship(
        "LeaseAgreement", back_populates="tenant", lazy="select"
    )
    invoices = db.relationship("Invoice", back_populates="tenant", lazy="select")
    payments = db.relationship("Payment", back_populates="tenant", lazy="select")
    complaints = db.relationship("Complaint", back_populates="tenant", lazy="select")
    maintenance_requests = db.relationship(
        "MaintenanceRequest", back_populates="tenant", lazy="select"
    )
