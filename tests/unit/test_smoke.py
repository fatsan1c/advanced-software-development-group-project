def test_pytest_runs():
    assert True


def test_can_import_validation_module():
    from pages.components import input_validation

    assert hasattr(input_validation, "is_email_valid")

