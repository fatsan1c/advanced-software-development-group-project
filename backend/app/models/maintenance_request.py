from __future__ import annotations

from ..extensions import db


class MaintenanceRequest(db.Model):
    __tablename__ = "maintenance_requests"

    request_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    apartment_ID = db.Column(
        db.Integer, db.ForeignKey("apartments.apartment_ID"), nullable=True
    )
    tenant_ID = db.Column(db.Integer, db.ForeignKey("tenants.tenant_ID"), nullable=True)
    issue_description = db.Column(db.String)
    priority_level = db.Column(db.Integer)
    reported_date = db.Column(db.String)
    scheduled_date = db.Column(db.String)
    completed = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float)

    apartment = db.relationship(
        "Apartment", back_populates="maintenance_requests", lazy="select"
    )
    tenant = db.relationship(
        "Tenant", back_populates="maintenance_requests", lazy="select"
    )
