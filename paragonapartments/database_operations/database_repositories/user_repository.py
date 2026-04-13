"""
Contributors: Aaron Antal-Bento (23013693), Ollie Churchley (23020494)

User Repository - All user-related database operations.
Handles authentication, user CRUD operations, and role management.
"""

from __future__ import annotations

from database_operations.database_repositories.base_repository import BaseRepository
from passlib.hash import sha256_crypt


class UsersRepository(BaseRepository):
    """Object-oriented data access for the users table."""

    TABLE = "users"
    ID_FIELD = "user_ID"
    ALLOWED_UPDATE_FIELDS = {"username", "password", "role", "location_ID"}

    def authenticate_user(self, username, password):
        """
        Authenticate a user by checking username and password against the database.

        Args:
            username (str): The username to check
            password (str): The password to check

        Returns:
            dict: User data if authentication successful, None otherwise
                  Example: {'user_ID': 1, 'username': 'john', 'role': 'Admin', 'city': 'Bristol'}
        """
        user = self.get_user_by_username(username)
        if user and sha256_crypt.verify(password, user["password"]):
            return {
                "user_ID": user["user_ID"],
                "username": user["username"],
                "role": user["role"],
                "city": user["city"],
            }
        return None

    def validate_credentials(self, username, password):
        """
        Validate if username and password combination exists.

        Args:
            username (str): The username to validate
            password (str): The password to validate

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        user = self.authenticate_user(username, password)
        return user is not None

    def get_user_by_username(self, username):
        """
        Get user details by username only.

        Args:
            username (str): The username to look up

        Returns:
            dict: User data if found, None otherwise
        """
        query = """
            SELECT users.user_ID, users.password, users.username, users.role, locations.city
            FROM users
            LEFT JOIN locations ON users.location_ID = locations.location_ID
            WHERE users.username = ?
        """
        return self._execute(query, (username,), fetch_one=True)

    def get_user_by_id(self, user_id):
        """
        Get user details by user ID.

        Args:
            user_id (int): The user ID to look up

        Returns:
            dict: User data if found, None otherwise
        """
        query = """
            SELECT users.user_ID, users.password, users.username, users.role, locations.city
            FROM users
            LEFT JOIN locations ON users.location_ID = locations.location_ID
            WHERE users.user_ID = ?
        """
        return self._execute(query, (user_id,), fetch_one=True)

    def get_user_role(self, username):
        """
        Get the role of a user by username.

        Args:
            username (str): The username to look up

        Returns:
            str: User role if found, None otherwise
        """
        user = self.get_user_by_username(username)
        return user["role"] if user else None

    def get_all_roles(self):
        """
        Get all distinct user roles from the database.

        Returns:
            list: List of role strings (e.g., ['Admin', 'Finance Manager', 'Manager'])
        """
        query = "SELECT DISTINCT role FROM users ORDER BY role"
        result = self._execute(query, fetch_all=True)
        return [row["role"] for row in result] if result else []

    def get_all_users(self):
        """
        Get all users from the database.

        Returns:
            list: List of user dictionaries, empty list if error
        """
        query = """
            SELECT users.user_ID, users.username, users.role, locations.city
            FROM users
            LEFT JOIN locations ON users.location_ID = locations.location_ID
        """
        return self._execute(query, fetch_all=True)

    def get_all_usernames(self):
        """
        Get all usernames from the database.

        Returns:
            list: List of username strings (e.g., ['john', 'jane', 'doe'])
        """
        result = self._get_all(columns=["username"], order_by="user_ID")
        return [row["username"] for row in result] if result else []

    def create_user(self, username, password, role, location_ID=None):
        """
        Create a new user in the database.

        Args:
            username (str): Username for the new user
            password (str): Plain text password (will be hashed)
            role (str): User role (Admin, Manager, Finance, etc.)
            location_ID (int, optional): Location ID for the user

        Returns:
            int: ID of newly created user, None if failed
        """
        hashed_password = sha256_crypt.hash(password)
        return self._insert(
            {
                "username": username,
                "password": hashed_password,
                "role": role,
                "location_ID": location_ID,
            },
        )

    def update_user(self, user_id, **kwargs):
        """
        Update user information.

        Args:
            user_id (int): ID of user to update
            **kwargs: Fields to update (username, password, role, location_ID)

        Returns:
            bool: True if successful, False otherwise
        """
        updates = {k: v for k, v in kwargs.items() if k in self.ALLOWED_UPDATE_FIELDS}

        if "password" in updates:
            updates["password"] = sha256_crypt.hash(updates["password"])

        if not updates:
            return False

        return self._update_by_id(
            user_id,
            updates,
            allowed_fields=self.ALLOWED_UPDATE_FIELDS,
        )

    def change_password(self, username, old_password, new_password):
        """
        Change a user's password.

        Args:
            username (str): Username of user whose password to change
            old_password (str): The current password to verify
            new_password (str): The new password (will be hashed)

        Returns:
            bool: True if successful, False otherwise
        """
        user = self.authenticate_user(username, old_password)
        if not user:
            return False
        user_id = user["user_ID"]

        hashed_password = sha256_crypt.hash(new_password)
        return self._update_by_id(
            user_id,
            {"password": hashed_password},
            allowed_fields={"password"},
        )

    def delete_user(self, user_id):
        """
        Delete a user from the database.

        Args:
            user_id (int): ID of user to delete

        Returns:
            bool: True if successful, False otherwise
        """
        return self._delete_by_id(user_id)
