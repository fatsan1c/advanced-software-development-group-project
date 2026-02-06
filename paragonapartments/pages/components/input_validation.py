from datetime import datetime, timedelta
import re

def is_email_valid(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def is_phone_valid(phone: str) -> bool:
    """Validate UK phone number format (07... or +44...)."""
    if not phone:
        return False
    # Remove spaces, hyphens, and parentheses
    clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    # UK mobile: 07XXXXXXXXX or +447XXXXXXXXX
    phone_regex = r'^(07\d{9}|\+447\d{9})$'
    return re.match(phone_regex, clean_phone) is not None

def is_date_of_birth_valid(dob: str) -> bool:
    """Validate date of birth format (YYYY-MM-DD) and check if age is at least 18."""
    if not dob:
        return False
    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d")
        # Check if date is not in the future
        if dob_date > datetime.now():
            return False
        # Check if at least 18 years old
        age_limit = datetime.now() - timedelta(days=18*365.25)
        return dob_date <= age_limit
    except ValueError:
        return False
    
def is_NI_number_valid(ni_number: str) -> bool:
    """Validate UK National Insurance number format (e.g., AB123456C)."""
    if not ni_number:
        return False
    # Remove spaces and convert to uppercase
    clean_ni = ni_number.replace(' ', '').upper()
    # UK NI format: 2 letters, 6 digits, 1 letter (A-D)
    # First letter cannot be D, F, I, Q, U, V
    # Second letter cannot be D, F, I, O, Q, U, V
    ni_regex = r'^[A-CEGHJ-PR-TW-Z]{1}[A-CEGHJ-NPR-TW-Z]{1}\d{6}[A-D]{1}$'
    return re.match(ni_regex, clean_ni) is not None

def is_annual_salary_valid(salary: str) -> bool:
    """Validate that annual salary is a positive number."""
    if not salary:
        return False
    try:
        salary_value = float(salary)
        return salary_value >= 0
    except ValueError:
        return False