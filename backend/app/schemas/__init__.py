"""
Backend schema layer.

Schemas define API input/output contracts:
- validate incoming payloads
- normalize request fields
- shape response payloads
"""

from .tenant_schema import validate_tenant_create_payload, tenant_response

__all__ = [
    "validate_tenant_create_payload",
    "tenant_response",
]

