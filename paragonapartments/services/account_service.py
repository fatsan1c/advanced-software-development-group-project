"""Contributors: Aaron Antal-Bento (23013693)

Account-related use-case service."""

from __future__ import annotations

from database_operations.database_repositories import users_repo


class AccountService:
    """Encapsulates account operations used by user session flows."""

    @staticmethod
    def change_password(username: str, old_password: str, new_password: str) -> bool:
        """Update a user's password and return whether it succeeded."""
        return users_repo.change_password(username, old_password, new_password)
    
    @staticmethod
    def authenticate_user(username: str, password: str):
        """Authenticate user credentials and return user data if valid."""
        return users_repo.authenticate_user(username, password)
