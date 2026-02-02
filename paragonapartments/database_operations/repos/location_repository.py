"""
Location Repository - All location-related database operations.
Handles location CRUD operations and location information retrieval.
"""

from database_operations.db_execute import execute_query

def get_location_by_id(location_id):
    """
    Get location details by location ID.
    
    Args:
        location_id (int): The location ID to look up
        
    Returns:
        dict: Location data if found, None otherwise
              Example: {'location_ID': 1, 'city': 'Bristol', 'address': '...'}
    """
    query = """
        SELECT location_ID, city, address
        FROM locations 
        WHERE location_ID = ?
    """
    return execute_query(query, (location_id,), fetch_one=True)


def get_location_by_city(city):
    """
    Get location details by city name.
    
    Args:
        city (str): The city name to look up
        
    Returns:
        dict: Location data if found, None otherwise
    """
    query = """
        SELECT location_ID, city, address
        FROM locations 
        WHERE city = ?
    """
    return execute_query(query, (city,), fetch_one=True)


def get_all_locations():
    """
    Get all locations from the database.
    
    Returns:
        list: List of location dictionaries, empty list if error
    """
    query = """
        SELECT location_ID, city, address
        FROM locations
        ORDER BY city
    """
    return execute_query(query, fetch_all=True)


def get_all_cities():
    """
    Get all city names from the database.
    
    Returns:
        list: List of city name strings (e.g., ['Bristol', 'Cardiff', 'London'])
    """
    query = "SELECT city FROM locations ORDER BY city"
    result = execute_query(query, fetch_all=True)
    return [row['city'] for row in result] if result else []


def get_location_id_by_city(city):
    """
    Get location ID by city name.
    
    Args:
        city (str): The city name to look up
        
    Returns:
        int: Location ID if found, None otherwise
    """
    location = get_location_by_city(city)
    return location['location_ID'] if location else None


def create_location(city, address=None):
    """
    Create a new location in the database.
    Requires: 'create' permission on 'locations' resource (checked by decorator)
    
    Args:
        city (str): City name for the new location
        address (str, optional): Physical address
        
    Returns:
        int: ID of newly created location, None if failed
    """
    query = """
        INSERT INTO locations (city, address)
        VALUES (?, ?)
    """
    return execute_query(query, (city, address), commit=True)


def update_location(location_id, **kwargs):
    """
    Update location information.
    Requires: 'update' permission on 'locations' resource (checked by decorator)
    
    Args:
        location_id (int): ID of location to update
        **kwargs: Fields to update (city, address)
        
    Returns:
        bool: True if successful, False otherwise
    """
    allowed_fields = ['city', 'address']
    updates = []
    values = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            updates.append(f"{field} = ?")
            values.append(value)
    
    if not updates:
        return False
    
    values.append(location_id)
    query = f"UPDATE locations SET {', '.join(updates)} WHERE location_ID = ?"
    
    result = execute_query(query, tuple(values), commit=True)
    return result is not None and result > 0


def delete_location(location_id):
    """
    Delete a location from the database.
    Requires: 'delete' permission on 'locations' resource (checked by decorator)
    
    Args:
        location_id (int): ID of location to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    query = "DELETE FROM locations WHERE location_ID = ?"
    result = execute_query(query, (location_id,), commit=True)
    return result is not None and result > 0


def get_location_stats(location_id):
    """
    Get statistics for a specific location.
    
    Args:
        location_id (int): The location ID
        
    Returns:
        dict: Statistics including user count, apartment count, etc.
    """
    query = """
        SELECT 
            l.location_ID,
            l.city,
            COUNT(DISTINCT u.user_ID) as user_count,
            COUNT(DISTINCT a.apartment_ID) as apartment_count
        FROM locations l
        LEFT JOIN users u ON l.location_ID = u.location_ID
        LEFT JOIN apartments a ON l.location_ID = a.location_ID
        WHERE l.location_ID = ?
        GROUP BY l.location_ID, l.city
    """
    return execute_query(query, (location_id,), fetch_one=True)
