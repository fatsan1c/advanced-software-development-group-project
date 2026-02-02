"""
Apartment Repository - All apartment-related database operations.
Handles apartment queries, occupancy tracking, and apartment management.
"""

from database_operations.db_execute import execute_query
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

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
    
    return canvas

def generate_financial_report():
     pass
    