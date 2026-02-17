from __future__ import annotations

from flask import Flask

from .config import Config
from .extensions import db
from .middlewares.errors import register_error_handlers
from .controllers import register_blueprints


def create_app(config_object: type[Config] = Config) -> Flask:
    """
    Flask app factory.

    This backend is introduced alongside the existing desktop client. Keep it
    small and resource-based (controllers/blueprints) and push business logic
    into services/.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # DB (optional for now, but models expect this)
    db.init_app(app)

    register_error_handlers(app)
    register_blueprints(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

