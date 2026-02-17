from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

# One global db handle for the backend app factory to init.
db = SQLAlchemy()

