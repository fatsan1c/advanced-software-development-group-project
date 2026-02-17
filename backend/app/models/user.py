from __future__ import annotations

from ..extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location_ID = db.Column(db.Integer, db.ForeignKey("locations.location_ID"), nullable=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String)

    location = db.relationship("Location", back_populates="users", lazy="select")

