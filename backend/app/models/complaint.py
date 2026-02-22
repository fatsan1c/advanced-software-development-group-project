from __future__ import annotations

from ..extensions import db


class Complaint(db.Model):
    __tablename__ = "complaint"

    complaint_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_ID = db.Column(db.Integer, db.ForeignKey("tenants.tenant_ID"))
    description = db.Column(db.String)
    date_submitted = db.Column(db.String)
    resolved = db.Column(db.Integer, default=0)

    tenant = db.relationship("Tenant", back_populates="complaints", lazy="select")
