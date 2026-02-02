"""
Repositories package for database access layer.
All database queries should go through these repository modules.
"""

from .repos.user_repository import (
    authenticate_user,
    validate_credentials,
    get_user_by_username,
    get_user_by_id,
    get_user_role,
    get_all_users,
    create_user,
    update_user,
    delete_user
)

from .repos.apartment_repository import (
    get_all_occupancy,
)

__all__ = [
    'authenticate_user',
    'validate_credentials',
    'get_user_by_username',
    'get_user_by_id',
    'get_user_role',
    'get_all_users',
    'create_user',
    'update_user',
    'delete_user',
    'get_all_occupancy',
]
