from __future__ import annotations

from ..extensions import db


class Location(db.Model):
    __tablename__ = "locations"

    location_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String, unique=True)
    address = db.Column(db.String, unique=True)

    apartments = db.relationship("Apartment", back_populates="location", lazy="select")
    users = db.relationship("User", back_populates="location", lazy="select")

