from __future__ import annotations

from ..extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    payment_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_ID = db.Column(db.Integer, db.ForeignKey("invoices.invoice_ID"))
    tenant_ID = db.Column(db.Integer, db.ForeignKey("tenants.tenant_ID"))
    payment_date = db.Column(db.String)
    amount = db.Column(db.Float)

    tenant = db.relationship("Tenant", back_populates="payments", lazy="select")
    invoice = db.relationship("Invoice", back_populates="payments", lazy="select")
