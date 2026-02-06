import pytest


def test_create_and_authenticate_user(seed_minimal_data):
    import database_operations.repos.user_repository as user_repo

    bristol_id = seed_minimal_data["locations"]["bristol"]

    user_id = user_repo.create_user("testuser", "secret123", "Manager", bristol_id)
    assert isinstance(user_id, int)

    auth = user_repo.authenticate_user("testuser", "secret123")
    assert auth is not None
    assert auth["username"] == "testuser"
    assert auth["role"] == "Manager"
    assert auth["city"] == "Bristol"

    assert user_repo.validate_credentials("testuser", "secret123") is True
    assert user_repo.validate_credentials("testuser", "wrong") is False


def test_update_user_and_change_password(seed_minimal_data):
    import database_operations.repos.user_repository as user_repo

    cardiff_id = seed_minimal_data["locations"]["cardiff"]
    user_id = user_repo.create_user("pwuser", "oldpw", "Admin", cardiff_id)

    # Update role + location
    assert user_repo.update_user(user_id, role="Finance", location_ID=None) is True
    updated = user_repo.get_user_by_id(user_id)
    assert updated["role"] == "Finance"
    assert updated["city"] is None

    # Change password
    assert user_repo.change_password("pwuser", "oldpw", "newpw") is True
    assert user_repo.validate_credentials("pwuser", "oldpw") is False
    assert user_repo.validate_credentials("pwuser", "newpw") is True


def test_delete_user(seed_minimal_data):
    import database_operations.repos.user_repository as user_repo

    user_id = user_repo.create_user("deluser", "pw", "Manager", None)
    assert user_repo.get_user_by_id(user_id) is not None

    assert user_repo.delete_user(user_id) is True
    assert user_repo.get_user_by_id(user_id) is None

