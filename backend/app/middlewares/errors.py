"""Error handlers for the Flask app."""

from __future__ import annotations

from flask import Flask, jsonify


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not_found", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "server_error", "message": "Internal server error"}), 500
