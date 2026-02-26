from datetime import datetime, timedelta, date
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


# ============================= Date Validation & Parsing =============================

def is_date_valid(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format.
    
    Args:
        date_str: Date string to validate
        format: Expected date format (default: "%Y-%m-%d")
        
    Returns:
        True if date is valid, False otherwise
    """
    if not date_str or not str(date_str).strip():
        return False
    try:
        datetime.strptime(str(date_str).strip(), format)
        return True
    except ValueError:
        return False


def parse_date(date_str, formats=None) -> date | None:
    """
    Parse date string with multiple format support.
    
    Args:
        date_str: Date string to parse
        formats: List of date formats to try. Defaults to ["%Y-%m-%d", "%d/%m/%Y"]
        
    Returns:
        date object if parsing succeeds, None otherwise
    """
    if not date_str or not str(date_str).strip():
        return None
    
    if formats is None:
        formats = ["%Y-%m-%d", "%d/%m/%Y"]
    
    s = str(date_str).strip()
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def normalize_date_to_db(date_str: str | None) -> str | None:
    """
    Normalize date string to database format (YYYY-MM-DD).
    Accepts multiple input formats and returns standardized format.
    Returns None for blank/invalid values.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Date string in YYYY-MM-DD format, or None if invalid
        
    Raises:
        ValueError: If date is provided but invalid
    """
    if date_str is None:
        return None
    s = str(date_str).strip()
    if not s:
        return None
    
    parsed = parse_date(s)
    if parsed is None:
        raise ValueError(f"Invalid date '{date_str}'. Expected YYYY-MM-DD or DD/MM/YYYY.")
    
    return parsed.strftime("%Y-%m-%d")


# ============================= Real-time Input Validators (for CTk entry widgets) =============================

def validate_number_input(value: str) -> bool:
    """
    Validate that input contains only digits (for real-time entry validation).
    Used with CTkEntry validatecommand.
    
    Args:
        value: Proposed input value
        
    Returns:
        True if valid (digits only or empty), False otherwise
    """
    return value.isdigit() or value == ""


def validate_currency_input(value: str) -> bool:
    """
    Validate currency input format (for real-time entry validation).
    Allows digits with optional decimal point and max 2 decimal places.
    Used with CTkEntry validatecommand.
    
    Args:
        value: Proposed input value
        
    Returns:
        True if valid currency format, False otherwise
        
    Examples:
        "123" -> True
        "123.45" -> True
        "123.456" -> False
        "123." -> True
        "" -> True
    """
    return re.match(r'^\d*\.?\d{0,2}$', value) is not None


def validate_date_input(value: str) -> bool:
    """
    Validate date input format YYYY-MM-DD (for real-time entry validation).
    Allows progressive typing: "2", "20", "202", "2026", "2026-", "2026-0", etc.
    Used with CTkEntry validatecommand.
    
    Args:
        value: Proposed input value
        
    Returns:
        True if valid progressive date format, False otherwise
        
    Examples:
        "" -> True
        "2026" -> True
        "2026-02" -> True
        "2026-02-26" -> True
        "2026-2-26" -> True (will be accepted for progressive typing)
        "abcd" -> False
    """
    return re.match(r'^(\d{0,4}(-\d{0,2}(-\d{0,2})?)?)?$', value) is not None


# ============================= Formatting Helpers =============================

def format_currency_display(value: float | str | None, currency_symbol: str = "£") -> str:
    """
    Format a numeric value as currency for display.
    
    Args:
        value: Numeric value to format
        currency_symbol: Currency symbol to use (default: "£")
        
    Returns:
        Formatted currency string
        
    Examples:
        12345.67 -> "£12,345.67"
        1000 -> "£1,000.00"
        None -> ""
        "" -> ""
    """
    if value is None or value == "":
        return ""
    try:
        num_value = float(value)
        return f"{currency_symbol}{num_value:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def strip_currency_formatting(value: str) -> str:
    """
    Remove currency formatting from a string for parsing.
    Removes currency symbols, commas, and extra spaces.
    
    Args:
        value: Formatted currency string
        
    Returns:
        Clean numeric string
        
    Examples:
        "£1,234.56" -> "1234.56"
        "£1,000" -> "1000"
        "1234.56" -> "1234.56"
    """
    if not value:
        return ""
    # Remove currency symbols and commas
    return value.replace("£", "").replace("$", "").replace("€", "").replace(",", "").strip()


def auto_format_date_entry(entry_widget):
    """
    Auto-format date entry widget to YYYY-MM-DD format as user types.
    Automatically inserts hyphens at appropriate positions.
    
    Args:
        entry_widget: CTkEntry widget to apply formatting to
        
    Usage:
        entry = ctk.CTkEntry(parent)
        auto_format_date_entry(entry)
    """
    def on_change(*args):
        current = entry_widget.get().replace("-", "")
        current = ''.join(filter(str.isdigit, current))[:8]
        formatted = current
        if len(current) > 4:
            formatted = current[:4] + "-" + current[4:]
        if len(current) > 6:
            formatted = formatted[:7] + "-" + formatted[7:]
        if entry_widget.get() != formatted:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, formatted)
    
    entry_widget.bind('<KeyRelease>', on_change)


def auto_format_currency_entry(entry_widget):
    """
    Auto-format currency entry widget to remove non-numeric characters except decimal point.
    Keeps only digits and one decimal point as user types.
    
    Args:
        entry_widget: CTkEntry widget to apply formatting to
        
    Usage:
        entry = ctk.CTkEntry(parent)
        auto_format_currency_entry(entry)
    """
    def on_change(*args):
        current = entry_widget.get().replace(",", "").replace("£", "").replace("$", "").replace("€", "")
        if current and not current.replace('.', '', 1).isdigit():
            current = ''.join(filter(lambda x: x.isdigit() or x == '.', current))
        if entry_widget.get() != current:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, current)
    
    entry_widget.bind('<KeyRelease>', on_change)
