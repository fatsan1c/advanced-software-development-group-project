def test_create_tenant_persists(seed_minimal_data):
    import database_operations.repos.tenants_repository as tenants_repo
    from database_operations.db_execute import execute_query

    tenant_id = tenants_repo.create_tenant(
        first_name="Charlie",
        last_name="Tenant",
        date_of_birth="1992-02-02",
        NI_number="AE123456C",
        email="charlie@example.com",
        phone="07111222333",
        occupation="Nurse",
        annual_salary=38000,
        right_to_rent="Y",
        credit_check="Passed",
        pets="N",
    )
    assert isinstance(tenant_id, int)

    row = execute_query(
        "SELECT tenant_ID, first_name, last_name, email FROM tenants WHERE tenant_ID = ?",
        (tenant_id,),
        fetch_one=True,
    )
    assert row is not None
    assert row["email"] == "charlie@example.com"

