from __future__ import annotations

import os
from pathlib import Path


class Config:
    """
    Minimal config for the Flask backend.

    Keep secrets/config in environment variables (12-factor).
    """

    ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "0") == "1"

    # If/when you wire database access, use this (SQLite by default).
    # Example: sqlite:///absolute/path/to/paragonapartments.db
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    # Flask-SQLAlchemy config (defaults to the same SQLite file used by the desktop app)
    _DEFAULT_SQLITE_PATH = (
        Path(__file__).resolve().parents[2]
        / "paragonapartments"
        / "database"
        / "paragonapartments.db"
    )
    SQLALCHEMY_DATABASE_URI: str = (
        DATABASE_URL or f"sqlite:///{_DEFAULT_SQLITE_PATH.as_posix()}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Auth placeholders (choose JWT or sessions later)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
