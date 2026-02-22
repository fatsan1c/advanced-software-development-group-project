def test_location_crud(seed_minimal_data):
    import database_operations.repos.location_repository as location_repo

    cities = location_repo.get_all_cities()
    assert "Bristol" in cities
    assert "Cardiff" in cities

    location_id = location_repo.create_location("Testville", "99 Example Rd")
    assert isinstance(location_id, int)

    loc = location_repo.get_location_by_id(location_id)
    assert loc["city"] == "Testville"

    assert location_repo.update_location(location_id, city="Testopolis") is True
    assert (
        location_repo.get_location_by_city("Testopolis")["location_ID"] == location_id
    )

    stats = location_repo.get_location_stats(location_id)
    assert stats["apartment_count"] == 0

    assert location_repo.delete_location(location_id) is True
    assert location_repo.get_location_by_id(location_id) is None
