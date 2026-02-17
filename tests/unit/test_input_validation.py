from datetime import datetime, timedelta


def test_email_validation():
    from pages.components.input_validation import is_email_valid

    assert is_email_valid("test@example.com") is True
    assert is_email_valid("name.surname+tag@domain.co.uk") is True

    assert is_email_valid("") is False
    assert is_email_valid("no-at-symbol.com") is False
    assert is_email_valid("a@b") is False
    assert is_email_valid("a@b.c") is False


def test_phone_validation():
    from pages.components.input_validation import is_phone_valid

    assert is_phone_valid("07123456789") is True
    assert is_phone_valid("+447123456789") is True

    # Formatting noise should be tolerated
    assert is_phone_valid("07 123 456 789") is True
    assert is_phone_valid("(07)123-456-789") is True
    assert is_phone_valid("+44 7123 456 789") is True

    assert is_phone_valid("") is False
    assert is_phone_valid("06123456789") is False
    assert is_phone_valid("0712345678") is False  # too short


def test_date_of_birth_validation_age_and_format():
    from pages.components.input_validation import is_date_of_birth_valid

    today = datetime.now()
    adult_dob = (today - timedelta(days=int(19 * 365.25))).strftime("%Y-%m-%d")
    underage_dob = (today - timedelta(days=int(17 * 365.25))).strftime("%Y-%m-%d")
    future_dob = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    assert is_date_of_birth_valid(adult_dob) is True
    assert is_date_of_birth_valid(underage_dob) is False
    assert is_date_of_birth_valid(future_dob) is False
    assert is_date_of_birth_valid("01-01-2000") is False


def test_ni_number_validation():
    from pages.components.input_validation import is_NI_number_valid

    assert is_NI_number_valid("AB123456A") is True
    assert is_NI_number_valid("ab123456c") is True  # normalization + casing
    assert is_NI_number_valid("AB 12 34 56 A") is True  # spaces are allowed

    assert is_NI_number_valid("") is False
    assert is_NI_number_valid("AB123456E") is False  # last letter must be A-D
    assert is_NI_number_valid("DF123456A") is False  # invalid first letter
    assert is_NI_number_valid("AD12345A") is False  # wrong digit count


def test_annual_salary_validation():
    from pages.components.input_validation import is_annual_salary_valid

    assert is_annual_salary_valid("0") is True
    assert is_annual_salary_valid("1234.56") is True
    assert is_annual_salary_valid("10000") is True

    assert is_annual_salary_valid("") is False
    assert is_annual_salary_valid("-1") is False
    assert is_annual_salary_valid("abc") is False

