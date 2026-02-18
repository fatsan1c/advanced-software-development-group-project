from database_operations.db_execute import execute_query
import database_operations.repos.location_repository as location_repo

def create_tenant(first_name, last_name, date_of_birth, NI_number, email, phone, occupation=None, annual_salary=None, pets='N', right_to_rent='N', credit_check='Pending'):
    """Create a new tenant in the database.
    
    Required fields:
        first_name - Tenant's first name
        last_name - Tenant's last name
        date_of_birth - Date of birth (YYYY-MM-DD)
        NI_number - National Insurance number
        email - Email address
        phone - Phone number
    Optional fields:
        occupation - Tenant's occupation
        annual_salary - Annual salary
        pets - Whether tenant has pets (Y/N)
        right_to_rent - Right to rent status (Y/N)
        credit_check - Credit check status (default: 'Pending')
    """
    query = """
    INSERT INTO tenants (first_name, last_name, date_of_birth, NI_number, email, phone, occupation, annual_salary, pets, right_to_rent, credit_check)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (first_name, last_name, date_of_birth, NI_number, email, phone, occupation, annual_salary, pets, right_to_rent, credit_check)
    return execute_query(query, params, commit=True)

def update_tenant(tenant_id, **kwargs):
    """Update tenant information in the database.
    
    Args:
        tenant_id - ID of the tenant to update
        **kwargs - Fields to update (first_name, last_name, date_of_birth, NI_number, 
                   email, phone, occupation, annual_salary, pets, right_to_rent, credit_check)
    
    Returns:
        True if successful, False otherwise
    """
    # Build dynamic UPDATE query based on provided fields
    valid_fields = ['first_name', 'last_name', 'date_of_birth', 'NI_number', 'email', 
                    'phone', 'occupation', 'annual_salary', 'pets', 'right_to_rent', 'credit_check']
    
    updates = []
    params = []
    
    for field, value in kwargs.items():
        if field in valid_fields:
            updates.append(f"{field} = ?")
            params.append(value)
    
    if not updates:
        return False
    
    params.append(tenant_id)
    query = f"UPDATE tenants SET {', '.join(updates)} WHERE tenant_ID = ?"
    
    return execute_query(query, tuple(params), commit=True)

def create_lease_agreement(tenant_id, apartment_id, start_date, end_date, monthly_rent):
    """Create a new lease agreement in the database.
    
    Args:
        tenant_id - ID of the tenant
        apartment_id - ID of the apartment
        start_date - Lease start date (YYYY-MM-DD)
        end_date - Lease end date (YYYY-MM-DD)
        monthly_rent - Monthly rent amount
    """
    query = """
    INSERT INTO lease_agreements (tenant_ID, apartment_ID, start_date, end_date, monthly_rent, active)
    VALUES (?, ?, ?, ?, ?, 1)
    """
    params = (tenant_id, apartment_id, start_date, end_date, monthly_rent)
    return execute_query(query, params, commit=True)

def get_last_tenant_id():
    """Get the ID of the most recently created tenant."""
    query = "SELECT MAX(tenant_ID) as last_id FROM tenants"
    result = execute_query(query, fetch_one=True)
    return result['last_id'] if result and result['last_id'] else None

def get_tenant_by_id(tenant_id, location=None):
    """Retrieve a tenant's information by their ID, optionally filtered by location."""
    if location:
        # Get location_ID from city name
        location_data = location_repo.get_location_by_city(location)
        if not location_data:
            return None
        location_id = location_data['location_ID']
        
        # Filter by location through lease_agreements and apartments
        query = """
        SELECT DISTINCT t.* 
        FROM tenants t
        INNER JOIN lease_agreements la ON t.tenant_ID = la.tenant_ID
        INNER JOIN apartments a ON la.apartment_ID = a.apartment_ID
        WHERE t.tenant_ID = ? AND a.location_ID = ?
        """
        return execute_query(query, (tenant_id, location_id), fetch_one=True)
    else:
        query = "SELECT * FROM tenants WHERE tenant_ID = ?"
        return execute_query(query, (tenant_id,), fetch_one=True)

def get_all_tenants(location=None):
    """Retrieve all tenants from the database, optionally filtered by location."""
    if location:
        # Get location_ID from city name
        location_data = location_repo.get_location_by_city(location)
        if not location_data:
            return []
        location_id = location_data['location_ID']
        
        # Filter by location through lease_agreements and apartments
        # Use subquery to ensure each tenant appears only once
        query = """
        SELECT t.* 
        FROM tenants t
        WHERE t.tenant_ID IN (
            SELECT DISTINCT la.tenant_ID 
            FROM lease_agreements la
            INNER JOIN apartments a ON la.apartment_ID = a.apartment_ID
            WHERE a.location_ID = ?
        )
        ORDER BY t.first_name, t.last_name
        """
        return execute_query(query, (location_id,), fetch_all=True)
    else:
        query = "SELECT * FROM tenants ORDER BY first_name, last_name"
        return execute_query(query, fetch_all=True)

def search_tenants(search_term, location=None):
    """Search for tenants by name, email, NI number, or phone, optionally filtered by location."""
    search_pattern = f"%{search_term}%"
    
    if location:
        # Get location_ID from city name
        location_data = location_repo.get_location_by_city(location)
        if not location_data:
            return []
        location_id = location_data['location_ID']
        
        # Filter by location through lease_agreements and apartments
        # Use subquery to ensure each tenant appears only once
        query = """
        SELECT t.* 
        FROM tenants t
        WHERE (t.first_name LIKE ? OR t.last_name LIKE ? OR t.email LIKE ? OR t.NI_number LIKE ? OR t.phone LIKE ?)
        AND t.tenant_ID IN (
            SELECT DISTINCT la.tenant_ID 
            FROM lease_agreements la
            INNER JOIN apartments a ON la.apartment_ID = a.apartment_ID
            WHERE a.location_ID = ?
        )
        ORDER BY t.first_name, t.last_name
        """
        return execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, location_id), fetch_all=True)
    else:
        query = """
        SELECT * FROM tenants 
        WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR NI_number LIKE ? OR phone LIKE ?
        ORDER BY first_name, last_name
        """
        return execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern), fetch_all=True)

def create_maintenance_request(apartment_id, tenant_id, issue_description, priority_level, reported_date):
    """Create a new maintenance request."""
    query = """
    INSERT INTO maintenance_requests (apartment_ID, tenant_ID, issue_description, priority_level, reported_date, completed)
    VALUES (?, ?, ?, ?, ?, 0)
    """
    params = (apartment_id, tenant_id, issue_description, priority_level, reported_date)
    return execute_query(query, params, commit=True)

def get_maintenance_requests_by_tenant(tenant_id):
    """Get all maintenance requests for a specific tenant."""
    query = """
    SELECT mr.*, a.apartment_address 
    FROM maintenance_requests mr
    LEFT JOIN apartments a ON mr.apartment_ID = a.apartment_ID
    WHERE mr.tenant_ID = ?
    ORDER BY mr.reported_date DESC
    """
    return execute_query(query, (tenant_id,), fetch_all=True)

def get_all_maintenance_requests(location=None):
    """Get all maintenance requests, optionally filtered by location."""
    if location:
        # Get location_ID from city name
        location_data = location_repo.get_location_by_city(location)
        if not location_data:
            return []
        location_id = location_data['location_ID']
        
        query = """
        SELECT mr.*, 
               (t.first_name || ' ' || t.last_name) as tenant_name,
               a.apartment_address
        FROM maintenance_requests mr
        LEFT JOIN tenants t ON mr.tenant_ID = t.tenant_ID
        LEFT JOIN apartments a ON mr.apartment_ID = a.apartment_ID
        WHERE a.location_ID = ?
        ORDER BY mr.completed, mr.priority_level DESC, mr.reported_date DESC
        """
        return execute_query(query, (location_id,), fetch_all=True)
    else:
        query = """
        SELECT mr.*, 
               (t.first_name || ' ' || t.last_name) as tenant_name,
               a.apartment_address
        FROM maintenance_requests mr
        LEFT JOIN tenants t ON mr.tenant_ID = t.tenant_ID
        LEFT JOIN apartments a ON mr.apartment_ID = a.apartment_ID
        ORDER BY mr.completed, mr.priority_level DESC, mr.reported_date DESC
        """
        return execute_query(query, fetch_all=True)

def create_complaint(tenant_id, description, date_submitted):
    """Create a new complaint."""
    query = """
    INSERT INTO complaint (tenant_ID, description, date_submitted, resolved)
    VALUES (?, ?, ?, 0)
    """
    params = (tenant_id, description, date_submitted)
    return execute_query(query, params, commit=True)

def get_complaints_by_tenant(tenant_id):
    """Get all complaints for a specific tenant."""
    query = """
    SELECT * FROM complaint
    WHERE tenant_ID = ?
    ORDER BY date_submitted DESC
    """
    return execute_query(query, (tenant_id,), fetch_all=True)

def get_all_complaints(location=None):
    """Get all complaints, optionally filtered by location."""
    if location:
        # Get location_ID from city name
        location_data = location_repo.get_location_by_city(location)
        if not location_data:
            return []
        location_id = location_data['location_ID']
        
        query = """
        SELECT c.*, 
               (t.first_name || ' ' || t.last_name) as tenant_name
        FROM complaint c
        LEFT JOIN tenants t ON c.tenant_ID = t.tenant_ID
        LEFT JOIN lease_agreements la ON t.tenant_ID = la.tenant_ID
        LEFT JOIN apartments a ON la.apartment_ID = a.apartment_ID
        WHERE a.location_ID = ?
        GROUP BY c.complaint_ID
        ORDER BY c.resolved, c.date_submitted DESC
        """
        return execute_query(query, (location_id,), fetch_all=True)
    else:
        query = """
        SELECT c.*, 
               (t.first_name || ' ' || t.last_name) as tenant_name
        FROM complaint c
        LEFT JOIN tenants t ON c.tenant_ID = t.tenant_ID
        ORDER BY c.resolved, c.date_submitted DESC
        """
        return execute_query(query, fetch_all=True)

def delete_maintenance_request(request_id):
    """Delete a maintenance request by ID."""
    query = "DELETE FROM maintenance_requests WHERE request_ID = ?"
    return execute_query(query, (request_id,), commit=True)

def update_maintenance_request_status(request_id, completed):
    """Update the completion status of a maintenance request."""
    query = "UPDATE maintenance_requests SET completed = ? WHERE request_ID = ?"
    return execute_query(query, (completed, request_id), commit=True)

def delete_complaint(complaint_id):
    """Delete a complaint by ID."""
    query = "DELETE FROM complaint WHERE complaint_ID = ?"
    return execute_query(query, (complaint_id,), commit=True)

def update_complaint_status(complaint_id, resolved):
    """Update the resolved status of a complaint."""
    query = "UPDATE complaint SET resolved = ? WHERE complaint_ID = ?"
    return execute_query(query, (resolved, complaint_id), commit=True)