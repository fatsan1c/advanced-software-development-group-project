from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.tenant import Tenant
from ..schemas import tenant_response, validate_tenant_create_payload


class TenantService:
    def list_tenants(self) -> list[dict]:
        tenants = Tenant.query.order_by(Tenant.tenant_ID.desc()).all()
        return [tenant_response(self._to_row(t)) for t in tenants]

    def create_tenant(self, payload: dict) -> tuple[bool, dict, int]:
        """
        Returns:
            (success, payload_or_error, status_code)
        """
        is_valid, errors = validate_tenant_create_payload(payload)
        if not is_valid:
            return False, {"error": "validation_error", "details": errors}, 400

        tenant = Tenant(
            first_name=str(payload["first_name"]).strip(),
            last_name=str(payload["last_name"]).strip(),
            date_of_birth=str(payload["date_of_birth"]).strip(),
            NI_number=str(payload["NI_number"]).strip(),
            email=str(payload["email"]).strip(),
            phone=str(payload["phone"]).strip(),
            occupation=payload.get("occupation"),
            annual_salary=(
                float(payload["annual_salary"])
                if payload.get("annual_salary") not in (None, "")
                else None
            ),
            pets=payload.get("pets", "N"),
            right_to_rent=payload.get("right_to_rent", "N"),
            credit_check=payload.get("credit_check", "Pending"),
        )

        try:
            db.session.add(tenant)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return (
                False,
                {"error": "conflict", "details": "NI number or email already exists."},
                409,
            )
        except Exception:
            db.session.rollback()
            return (
                False,
                {"error": "server_error", "details": "Failed to create tenant."},
                500,
            )

        return True, {"tenant": tenant_response(self._to_row(tenant))}, 201

    @staticmethod
    def _to_row(tenant: Tenant) -> dict:
        return {
            "tenant_ID": tenant.tenant_ID,
            "first_name": tenant.first_name,
            "last_name": tenant.last_name,
            "date_of_birth": tenant.date_of_birth,
            "NI_number": tenant.NI_number,
            "email": tenant.email,
            "phone": tenant.phone,
            "occupation": tenant.occupation,
            "annual_salary": tenant.annual_salary,
            "pets": tenant.pets,
            "right_to_rent": tenant.right_to_rent,
            "credit_check": tenant.credit_check,
        }
