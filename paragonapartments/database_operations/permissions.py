"""
Role-Based Access Control (RBAC) Module
Handles permission checking and role-based access control for the application.
"""

from functools import wraps


# Define role hierarchy (higher number = more privileges)
ROLE_HIERARCHY = {
    'manager': 5,      # Full access to everything
    'admin': 4,        # Location-specific admin
    'finance': 3,      # Financial operations
    'frontdesk': 2,    # Basic operations
    'maintenance': 2,  # Maintenance-specific operations
    'guest': 1,        # Read-only access
    None: 0            # No access
}

# Define permissions for each role
ROLE_PERMISSIONS = {
    'manager': {
        'users': ['create', 'read', 'update', 'delete'],
        'apartments': ['create', 'read', 'update', 'delete'],
        'tenants': ['create', 'read', 'update', 'delete'],
        'leases': ['create', 'read', 'update', 'delete'],
        'invoices': ['create', 'read', 'update', 'delete'],
        'payments': ['create', 'read', 'update', 'delete'],
        'maintenance': ['create', 'read', 'update', 'delete'],
        'complaints': ['create', 'read', 'update', 'delete'],
        'reports': ['view', 'export']
    },
    'admin': {
        'users': ['create', 'read', 'update'],  # Can't delete users
        'apartments': ['create', 'read', 'update', 'delete'],
        'tenants': ['create', 'read', 'update', 'delete'],
        'leases': ['create', 'read', 'update', 'delete'],
        'invoices': ['create', 'read', 'update'],
        'payments': ['create', 'read', 'update'],
        'maintenance': ['create', 'read', 'update', 'delete'],
        'complaints': ['create', 'read', 'update', 'delete'],
        'reports': ['view', 'export']
    },
    'finance': {
        'apartments': ['read'],
        'tenants': ['read'],
        'leases': ['read'],
        'invoices': ['create', 'read', 'update', 'delete'],
        'payments': ['create', 'read', 'update', 'delete'],
        'reports': ['view', 'export']
    },
    'frontdesk': {
        'apartments': ['read'],
        'tenants': ['create', 'read', 'update'],
        'leases': ['create', 'read'],
        'invoices': ['read'],
        'payments': ['read'],
        'maintenance': ['create', 'read'],
        'complaints': ['create', 'read']
    },
    'maintenance': {
        'apartments': ['read'],
        'tenants': ['read'],
        'maintenance': ['read', 'update'],
        'complaints': ['read']
    },
    'guest': {
        'apartments': ['read'],
        'tenants': ['read'],
        'leases': ['read'],
        'invoices': ['read'],
        'payments': ['read'],
        'maintenance': ['read'],
        'complaints': ['read']
    }
}


class PermissionError(Exception):
    """Raised when user doesn't have required permission."""
    pass


def has_permission(user, resource, action):
    """
    Check if a user has permission to perform an action on a resource.
    
    Args:
        user (dict): User object with 'role' key
        resource (str): Resource type (e.g., 'users', 'apartments')
        action (str): Action to perform (e.g., 'create', 'read', 'update', 'delete')
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    if user is None:
        return False
    
    role = user.get('role')
    if role not in ROLE_PERMISSIONS:
        return False
    
    role_perms = ROLE_PERMISSIONS[role]
    if resource not in role_perms:
        return False
    
    return action in role_perms[resource]


def require_permission(resource, action):
    """
    Decorator to require specific permission for a function.
    
    Args:
        resource (str): Resource type (e.g., 'users', 'apartments')
        action (str): Required action (e.g., 'create', 'read', 'update', 'delete')
        
    Usage:
        @require_permission('users', 'delete')
        def delete_user(current_user, user_id):
            # Function code here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(current_user, *args, **kwargs):
            if not has_permission(current_user, resource, action):
                user_role = current_user.get('role', 'unknown') if current_user else 'None'
                raise PermissionError(
                    f"User with role '{user_role}' does not have permission to "
                    f"'{action}' on '{resource}'"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(*allowed_roles):
    """
    Decorator to require specific role(s) for a function.
    
    Args:
        *allowed_roles: One or more role names that are allowed
        
    Usage:
        @require_role('manager', 'admin')
        def sensitive_operation(current_user, data):
            # Function code here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(current_user, *args, **kwargs):
            if current_user is None:
                raise PermissionError("User not authenticated")
            
            user_role = current_user.get('role')
            if user_role not in allowed_roles:
                raise PermissionError(
                    f"User with role '{user_role}' is not authorized. "
                    f"Required roles: {', '.join(allowed_roles)}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role_level(min_level):
    """
    Decorator to require minimum role hierarchy level.
    
    Args:
        min_level (int): Minimum hierarchy level required (see ROLE_HIERARCHY)
        
    Usage:
        @require_role_level(4)  # Requires admin or manager
        def admin_function(current_user):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(current_user, *args, **kwargs):
            if current_user is None:
                raise PermissionError("User not authenticated")
            
            user_role = current_user.get('role')
            user_level = ROLE_HIERARCHY.get(user_role, 0)
            
            if user_level < min_level:
                raise PermissionError(
                    f"Insufficient privileges. Role '{user_role}' has level {user_level}, "
                    f"but level {min_level} or higher is required"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_location_access(user, location_id):
    """
    Check if user has access to a specific location.
    Managers have access to all locations, others only to their assigned location.
    
    Args:
        user (dict): User object with 'role' and 'location_ID' keys
        location_id (int): Location ID to check access for
        
    Returns:
        bool: True if user has access, False otherwise
    """
    if user is None:
        return False
    
    # Managers and finance have access to all locations
    if user.get('role') in ['manager', 'finance']:
        return True
    
    # Others only have access to their assigned location
    return user.get('location_ID') == location_id


def require_location_access(func):
    """
    Decorator to check if user has access to the location they're trying to access.
    Expects location_id as a keyword argument or second positional argument.
    
    Usage:
        @require_location_access
        def get_location_data(current_user, location_id):
            pass
    """
    @wraps(func)
    def wrapper(current_user, *args, **kwargs):
        # Try to get location_id from kwargs or args
        location_id = kwargs.get('location_id')
        if location_id is None and len(args) > 0:
            location_id = args[0]
        
        if location_id is not None and not check_location_access(current_user, location_id):
            raise PermissionError(
                f"User does not have access to location {location_id}"
            )
        
        return func(*args, **kwargs)
    return wrapper


def get_allowed_actions(user, resource):
    """
    Get list of allowed actions for a user on a resource.
    
    Args:
        user (dict): User object with 'role' key
        resource (str): Resource type
        
    Returns:
        list: List of allowed action strings
    """
    if user is None:
        return []
    
    role = user.get('role')
    if role not in ROLE_PERMISSIONS:
        return []
    
    role_perms = ROLE_PERMISSIONS[role]
    return role_perms.get(resource, [])


def can_access_resource(user, resource):
    """
    Check if user has any access to a resource.
    
    Args:
        user (dict): User object with 'role' key
        resource (str): Resource type
        
    Returns:
        bool: True if user has any access, False otherwise
    """
    return len(get_allowed_actions(user, resource)) > 0
