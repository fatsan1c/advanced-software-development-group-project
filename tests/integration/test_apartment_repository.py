def test_occupancy_and_revenue(seed_minimal_data):
    import database_operations.repos.apartment_repository as apartment_repo

    # Seed data has two occupied apartments (one per location)
    assert apartment_repo.get_all_occupancy() == 2
    assert apartment_repo.get_total_apartments() == 2

    assert apartment_repo.get_all_occupancy("Bristol") == 1
    assert apartment_repo.get_total_apartments("Bristol") == 1

    assert apartment_repo.get_monthly_revenue("Bristol") == 900.0
    assert apartment_repo.get_potential_revenue("Bristol") == 900.0


def test_apartment_crud(seed_minimal_data):
    import database_operations.repos.apartment_repository as apartment_repo
    import database_operations.repos.location_repository as location_repo

    bristol_id = location_repo.get_location_id_by_city("Bristol")

    ok = apartment_repo.create_apartment(bristol_id, "New Flat", 3, 1500.0, 0)
    assert ok is True

    apartments = apartment_repo.get_all_apartments()
    new_row = next(a for a in apartments if a["apartment_address"] == "New Flat")
    apt_id = int(new_row["apartment_ID"])

    assert apartment_repo.update_apartment(apt_id, occupied=1) is True
    assert apartment_repo.delete_apartment(apt_id) is True

