"""Controllers (blueprints) for the API."""

from __future__ import annotations

from flask import Flask

from .tenant_controller import tenant_bp


def register_blueprints(app: Flask) -> None:
    """Register all blueprints with the app."""
    app.register_blueprint(tenant_bp)
