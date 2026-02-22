from __future__ import annotations

from flask import Blueprint, request

from ..middlewares.roles import require_role
from ..services.tenant_service import TenantService

tenant_bp = Blueprint("tenants", __name__, url_prefix="/tenants")
_service = TenantService()


@tenant_bp.get("/")
@require_role("admin", "manager", "frontdesk", "finance", "maintenance")
def list_tenants():
    return {"tenants": _service.list_tenants()}


@tenant_bp.post("/")
@require_role("admin", "frontdesk", "manager")
def create_tenant():
    payload = request.get_json(silent=True) or {}
    success, result, status = _service.create_tenant(payload)
    return result, status
