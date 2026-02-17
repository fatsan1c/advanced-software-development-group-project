from __future__ import annotations

from ..extensions import db


class Invoice(db.Model):
    __tablename__ = "invoices"

    invoice_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_ID = db.Column(db.Integer, db.ForeignKey("tenants.tenant_ID"))
    amount_due = db.Column(db.Float)
    due_date = db.Column(db.String)
    issue_date = db.Column(db.String)
    paid = db.Column(db.Integer, default=0)

    tenant = db.relationship("Tenant", back_populates="invoices", lazy="select")
    payments = db.relationship("Payment", back_populates="invoice", lazy="select")

