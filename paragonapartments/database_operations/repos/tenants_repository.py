from database_operations.db_execute import execute_query

def create_tenant(first_name, last_name, date_of_birth, NI_number, email, phone, occupation, annual_salary, right_to_rent, credit_check, pets='N'):
    """Create a new tenant in the database.
    
    Required fields:
        first_name, last_name - Tenant's name split into separate fields
        date_of_birth, NI_number, email, phone - Basic tenant info
        occupation - Tenant's job/employment
        annual_salary - Yearly income (for affordability assessment)
        right_to_rent - Legal requirement in UK (Y/N)
        credit_check - Tenant screening status (Passed/Failed/Pending)
    
    Optional fields:
        pets - Defaults to 'N' if not specified
    """
    query = """
    INSERT INTO tenants (first_name, last_name, date_of_birth, NI_number, email, phone, occupation, annual_salary, pets, right_to_rent, credit_check)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (first_name, last_name, date_of_birth, NI_number, email, phone, occupation, annual_salary, pets, right_to_rent, credit_check)
    execute_query(query, params)

def get_all_tenant_names():
    """Retrieve all tenant names from the database."""
    query = "SELECT first_name, last_name, tenant_ID FROM tenants"
    return execute_query(query, fetch_all=True)
