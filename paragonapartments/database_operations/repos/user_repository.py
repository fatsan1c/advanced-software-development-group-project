"""
User Repository - All user-related database operations.
Handles authentication, user CRUD operations, and role management.
"""

from database_operations.db_execute import execute_query


def authenticate_user(username, password):
    """
    Authenticate a user by checking username and password against the database.
    
    Args:
        username (str): The username to check
        password (str): The password to check
        
    Returns:
        dict: User data if authentication successful, None otherwise
              Example: {'username': 'john', 'role': 'Admin', 'city': 'Bristol'}
    """
    query = """
        SELECT users.username, users.role, users.location_ID, locations.city
        FROM users
        LEFT JOIN locations ON users.location_ID = locations.location_ID
        WHERE users.username = ? AND users.password = ?
    """
    return execute_query(query, (username, password), fetch_one=True)


def validate_credentials(username, password):
    """
    Validate if username and password combination exists.
    
    Args:
        username (str): The username to validate
        password (str): The password to validate
        
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    user = authenticate_user(username, password)
    return user is not None


def get_user_by_username(username):
    """
    Get user details by username only.
    
    Args:
        username (str): The username to look up
        
    Returns:
        dict: User data if found, None otherwise
    """
    query = """
        SELECT users.user_ID, users.username, users.role, locations.city
        FROM users 
        LEFT JOIN locations ON users.location_ID = locations.location_ID
        WHERE users.username = ?
    """
    return execute_query(query, (username,), fetch_one=True)


def get_user_by_id(user_id):
    """
    Get user details by user ID.
    
    Args:
        user_id (int): The user ID to look up
        
    Returns:
        dict: User data if found, None otherwise
    """
    query = """
        SELECT users.user_ID, users.username, users.role, locations.city
        FROM users 
        LEFT JOIN locations ON users.location_ID = locations.location_ID
        WHERE users.user_ID = ?
    """
    return execute_query(query, (user_id,), fetch_one=True)


def get_user_role(username):
    """
    Get the role of a user by username.
    
    Args:
        username (str): The username to look up
        
    Returns:
        str: User role if found, None otherwise
    """
    user = get_user_by_username(username)
    return user['role'] if user else None


def get_all_roles():
    """
    Get all distinct user roles from the database.
    Requires: 'read' permission on 'users' resource (checked by decorator)
    
    Returns:
        list: List of role strings (e.g., ['Admin', 'Finance Manager', 'Manager'])
    """
    query = "SELECT DISTINCT role FROM users ORDER BY role"
    result = execute_query(query, fetch_all=True)
    return [row['role'] for row in result] if result else []


def get_all_users():
    """
    Get all users from the database.
    Requires: 'read' permission on 'users' resource (checked by decorator)
    
    Returns:
        list: List of user dictionaries, empty list if error
    """
    query = """
        SELECT users.user_ID, users.username, users.role, locations.city
        FROM users
        LEFT JOIN locations ON users.location_ID = locations.location_ID
    """
    return execute_query(query, fetch_all=True)

def get_all_usernames():
    """
    Get all usernames from the database.
    
    Returns:
        list: List of username strings (e.g., ['john', 'jane', 'doe'])
    """
    query = "SELECT username FROM users ORDER BY user_ID"
    result = execute_query(query, fetch_all=True)
    return [row['username'] for row in result] if result else []

def create_user(username, password, role, location_ID=None):
    """
    Create a new user in the database.
    Requires: 'create' permission on 'users' resource (checked by decorator)
    
    Args:
        username (str): Username for the new user
        password (str): Password (TODO: should be hashed)
        role (str): User role (Admin, Manager, Finance, etc.)
        location_ID (int, optional): Location ID for the user
        
    Returns:
        int: ID of newly created user, None if failed
    """
    query = """
        INSERT INTO users (username, password, role, location_ID)
        VALUES (?, ?, ?, ?)
    """
    return execute_query(query, (username, password, role, location_ID), commit=True)


def update_user(user_id, **kwargs):
    """
    Update user information.
    Requires: 'update' permission on 'users' resource (checked by decorator)
    
    Args:
        user_id (int): ID of user to update
        **kwargs: Fields to update (username, password, role, location_ID)
        
    Returns:
        bool: True if successful, False otherwise
    """
    allowed_fields = ['username', 'password', 'role', 'location_ID']
    updates = []
    values = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            updates.append(f"{field} = ?")
            values.append(value)
    
    if not updates:
        return False
    
    values.append(user_id)
    query = f"UPDATE users SET {', '.join(updates)} WHERE user_ID = ?"
    
    result = execute_query(query, tuple(values), commit=True)
    return result is not None and result > 0


def delete_user(user_id):
    """
    Delete a user from the database.
    Requires: 'manager' role (checked by decorator)
    
    Args:
        user_id (int): ID of user to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    query = "DELETE FROM users WHERE user_ID = ?"
    result = execute_query(query, (user_id,), commit=True)
    return result is not None and result > 0