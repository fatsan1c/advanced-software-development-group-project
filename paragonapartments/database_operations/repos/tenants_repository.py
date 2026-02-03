from database_operations.db_execute import execute_query

def create_tenant(name, date_of_birth, NI_number, email, phone, occupation, annual_salary, right_to_rent, credit_check, pets='N'):
    """Create a new tenant in the database.
    
    Required fields:
        name, date_of_birth, NI_number, email, phone - Basic tenant info
        occupation - Tenant's job/employment
        annual_salary - Yearly income (for affordability assessment)
        right_to_rent - Legal requirement in UK (Y/N)
        credit_check - Tenant screening status (Passed/Failed/Pending)
    
    Optional fields:
        pets - Defaults to 'N' if not specified
    """
    query = """
    INSERT INTO tenants (name, date_of_birth, NI_number, email, phone, occupation, annual_salary, pets, right_to_rent, credit_check)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (name, date_of_birth, NI_number, email, phone, occupation, annual_salary, pets, right_to_rent, credit_check)
    execute_query(query, params)