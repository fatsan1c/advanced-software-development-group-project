"""
Apartment Repository - All apartment-related database operations.
Handles apartment queries, occupancy tracking, and apartment management.
"""

from database_operations.db_execute import execute_query
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# This function is a workaround to prevent errors when the parent widget is closed while the graph is still active
def _setup_graph_cleanup(parent, canvas, fig):
    """
    Set up cleanup for matplotlib canvas to prevent callback errors.
    """
    def cleanup(event=None):
        try:
            canvas.flush_events()
            plt.close(fig)
        except:
            pass
    
    # Bind the cleanup function to the parent widget's destroy event
    parent.bind('<Destroy>', cleanup, add='+')

def get_all_occupancy(location=None):
    """
    Retrieve count of occupied apartments from the database.
    
    Args:
        location (str, optional): City name to filter by. If None, returns all occupied apartments.
    
    Returns:
        int: Number of occupied apartments (where occupied = 1)
    """
    if location and location.lower() != "all":
        query = """
            SELECT a.apartment_ID 
            FROM apartments a
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE a.occupied = 1 AND l.city = ?
        """
        results = execute_query(query, (location,), fetch_all=True)
    else:
        query = """
            SELECT apartment_ID FROM apartments WHERE occupied = 1
        """
        results = execute_query(query, fetch_all=True)
    
    return len(results) if results else 0


def get_total_apartments(location=None):
    """
    Retrieve total count of all apartments from the database.
    
    Args:
        location (str, optional): City name to filter by. If None, returns all apartments.
    
    Returns:
        int: Total number of apartments
    """
    if location and location.lower() != "all":
        query = """
            SELECT a.apartment_ID 
            FROM apartments a
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE l.city = ?
        """
        results = execute_query(query, (location,), fetch_all=True)
    else:
        query = """
            SELECT apartment_ID FROM apartments
        """
        results = execute_query(query, fetch_all=True)
    
    return len(results) if results else 0

def create_occupancy_graph(parent, location=None):
    """
    Create and embed a bar graph of occupied vs total apartments in a tkinter widget.
    
    Args:
        parent: The parent widget to embed the graph in
        location (str, optional): City name to filter by. If None, shows data for all apartments.
    """
    occupied_count = get_all_occupancy(location)
    total_count = get_total_apartments(location)
    vacant_count = total_count - occupied_count

    labels = ['Occupied', 'Vacant']
    counts = [occupied_count, vacant_count]
    colors = ['#4CAF50', '#F44336']  # Green for occupied, Red for vacant

    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(labels, counts, color=colors)
    
    # Add counts on top of bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, int(yval), ha='center', va='bottom')

    title_location = location if location and location.lower() != "all" else "All Locations"
    ax.set_title(f'Apartment Occupancy in {title_location}', fontsize=16, fontweight='bold')
    ax.set_ylabel('Number of Apartments', fontsize=12)
    ax.set_ylim(0, max(counts) + 10 if counts else 10)
    
    # Embed in tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
    
    _setup_graph_cleanup(parent, canvas, fig)
    
    return canvas


def get_monthly_revenue(location=None):
    """
    Calculate total monthly revenue from occupied apartments.
    
    Args:
        location (str, optional): City name to filter by. If None, returns revenue for all apartments.
    
    Returns:
        float: Total monthly revenue from occupied apartments
    """
    if location and location.lower() != "all":
        query = """
            SELECT SUM(a.monthly_rent) as total_revenue
            FROM apartments a
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE a.occupied = 1 AND l.city = ?
        """
        result = execute_query(query, (location,), fetch_one=True)
    else:
        query = """
            SELECT SUM(monthly_rent) as total_revenue
            FROM apartments
            WHERE occupied = 1
        """
        result = execute_query(query, fetch_one=True)
    
    return result['total_revenue'] if result and result['total_revenue'] else 0


def get_potential_revenue(location=None):
    """
    Calculate potential monthly revenue if all apartments were occupied.
    
    Args:
        location (str, optional): City name to filter by. If None, returns potential revenue for all apartments.
    
    Returns:
        float: Potential monthly revenue from all apartments
    """
    if location and location.lower() != "all":
        query = """
            SELECT SUM(a.monthly_rent) as potential_revenue
            FROM apartments a
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE l.city = ?
        """
        result = execute_query(query, (location,), fetch_one=True)
    else:
        query = """
            SELECT SUM(monthly_rent) as potential_revenue
            FROM apartments
        """
        result = execute_query(query, fetch_one=True)
    
    return result['potential_revenue'] if result and result['potential_revenue'] else 0


def create_performance_graph(parent, location=None):
    """
    Create and embed a bar graph of actual vs potential monthly revenue in a tkinter widget.
    
    Args:
        parent: The parent widget to embed the graph in
        location (str, optional): City name to filter by. If None, shows data for all apartments.
    """
    actual_revenue = get_monthly_revenue(location)
    potential_revenue = get_potential_revenue(location)
    lost_revenue = potential_revenue - actual_revenue
    showing_all = location is None or location.lower() == "all"

    labels = ['Actual Revenue', 'Lost Revenue']
    counts = [actual_revenue, lost_revenue]
    colors = ['#4CAF50', '#FF9800']  # Green for actual, Orange for lost

    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(labels, counts, color=colors)
    
    # Add amounts on top of bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 50, f'£{int(yval):,}', ha='center', va='bottom', fontsize=10)

    title_location = location if not showing_all else "All Locations"
    ax.set_title(f'Monthly Revenue Performance in {title_location}', fontsize=16, fontweight='bold')
    ax.set_ylabel('Revenue (£)', fontsize=12)
    ax.set_ylim(0, max(counts) + (2000 if showing_all else 500) if counts else 500)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{int(x):,}'))
    
    # Embed in tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
    
    _setup_graph_cleanup(parent, canvas, fig)
    
    return canvas


def generate_performance_report():
     pass
    
def get_all_apartments():
    """
    Get all apartments from the database.
    
    Returns:
        list: List of apartment dictionaries, empty list if error
    """
    query = """
        SELECT a.apartment_ID, l.city, a.apartment_address, a.number_of_beds, a.monthly_rent, 
               CASE WHEN a.occupied = 1 THEN 'Occupied' ELSE 'Vacant' END AS status
        FROM apartments a
        JOIN locations l ON a.location_ID = l.location_ID
        ORDER BY l.city, a.apartment_address
    """
    return execute_query(query, fetch_all=True)

def create_apartment(location_ID, apartment_address, number_of_beds, monthly_rent, occupied):
    """
    Create a new apartment in the database.
    
    Args:
        apartment_address (str): Address of the apartment
        number_of_beds (int): Number of beds in the apartment
        monthly_rent (float): Monthly rent amount
        occupied (int): 1 if occupied, 0 if vacant
        location_ID (int): Location ID for the apartment
        
    Returns:
        bool: True if creation was successful, False otherwise
    """
    
    query = """
        INSERT INTO apartments (apartment_address, number_of_beds, monthly_rent, occupied, location_ID)
        VALUES (?, ?, ?, ?, ?)
    """
    params = (apartment_address, number_of_beds, monthly_rent, occupied, location_ID)
    
    result = execute_query(query, params, commit=True)
    return result is not None

def update_apartment(apartment_id, **kwargs):
    """
    Update apartment information.
    
    Args:
        apartment_id (int): ID of apartment to update
        **kwargs: Fields to update (apartment_address, number_of_beds, monthly_rent, occupied, location_ID)
        
    Returns:
        bool: True if successful, False otherwise
    """
    fields = []
    params = []
    
    for key, value in kwargs.items():
        fields.append(f"{key} = ?")
        params.append(value)
    
    params.append(apartment_id)
    set_clause = ", ".join(fields)
    
    query = f"""
        UPDATE apartments
        SET {set_clause}
        WHERE apartment_ID = ?
    """
    
    result = execute_query(query, tuple(params), commit=True)
    return result is not None

def delete_apartment(apartment_id):
    """
    Delete an apartment from the database.
    
    Args:
        apartment_id (int): ID of apartment to delete
    """
    query = """
        DELETE FROM apartments
        WHERE apartment_ID = ?
    """
    result = execute_query(query, (apartment_id,), commit=True)
    return result is not None