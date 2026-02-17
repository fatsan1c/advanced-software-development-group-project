from __future__ import annotations

from ..extensions import db


class LeaseAgreement(db.Model):
    __tablename__ = "lease_agreements"

    lease_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_ID = db.Column(db.Integer, db.ForeignKey("tenants.tenant_ID"))
    apartment_ID = db.Column(db.Integer, db.ForeignKey("apartments.apartment_ID"))
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    monthly_rent = db.Column(db.Float)
    active = db.Column(db.Integer, default=1)

    tenant = db.relationship("Tenant", back_populates="lease_agreements", lazy="select")
    apartment = db.relationship("Apartment", back_populates="lease_agreements", lazy="select")

