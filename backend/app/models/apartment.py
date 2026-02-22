from __future__ import annotations

from ..extensions import db


class Apartment(db.Model):
    __tablename__ = "apartments"

    apartment_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_ID = db.Column(db.Integer, db.ForeignKey("locations.location_ID"))
    apartment_address = db.Column(db.String)
    number_of_beds = db.Column(db.Integer)
    monthly_rent = db.Column(db.Float)
    occupied = db.Column(db.Integer, default=0)

    location = db.relationship("Location", back_populates="apartments", lazy="select")
    lease_agreements = db.relationship(
        "LeaseAgreement", back_populates="apartment", lazy="select"
    )
    maintenance_requests = db.relationship(
        "MaintenanceRequest", back_populates="apartment", lazy="select"
    )
