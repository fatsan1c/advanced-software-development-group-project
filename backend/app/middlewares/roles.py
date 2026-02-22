"""Role-based access control for API endpoints."""

from __future__ import annotations

from functools import wraps


def require_role(*allowed_roles: str):
    """
    Decorator to require one of the given roles for the endpoint.
    Currently a pass-through (no auth wired); add JWT/session checks when auth is implemented.
    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # TODO: Check request headers/session for user role when auth is implemented
            return f(*args, **kwargs)

        return wrapped

    return decorator
