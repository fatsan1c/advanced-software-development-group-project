"""
Apartment Repository - All apartment-related database operations.
Handles apartment queries, occupancy tracking, and apartment management.
"""

import calendar as _calendar
from database_operations.db_execute import execute_query
from datetime import date as _date, datetime as _datetime, timedelta as _timedelta
import numpy as np
from pages.components.chart_utils import (
    ACCENT_GREEN,
    ACCENT_ORANGE,
    ACCENT_RED,
    create_bar_chart,
    create_trend_chart,
)


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


def _normalize_location(location):
    """Normalize location: None/'all' -> None, else city string."""
    if not location:
        return None
    loc = str(location).strip()
    if not loc or loc.lower() in {"all", "all locations"}:
        return None
    return loc


def _parse_date(date_str):
    """Parse YYYY-MM-DD or DD/MM/YYYY to date. Returns None if invalid."""
    if not date_str or not str(date_str).strip():
        return None
    s = str(date_str).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return _datetime.strptime(s, fmt).date()
        except Exception:
            continue
    return None


def _get_earliest_lease_date(location=None):
    """Earliest lease start_date for location."""
    city = _normalize_location(location)
    query = """
        SELECT MIN(date(la.start_date)) AS min_date
        FROM lease_agreements la
        JOIN apartments a ON la.apartment_ID = a.apartment_ID
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE la.start_date IS NOT NULL
    """ + (" AND l.city = ?" if city else "")
    params = (city,) if city else None
    row = execute_query(query, params, fetch_one=True) or {}
    raw = row.get("min_date")
    if not raw:
        return None
    try:
        return _datetime.strptime(str(raw), "%Y-%m-%d").date()
    except Exception:
        return None


def _get_latest_lease_date(location=None):
    """Latest lease end_date for location."""
    city = _normalize_location(location)
    query = """
        SELECT MAX(date(la.end_date)) AS max_date
        FROM lease_agreements la
        JOIN apartments a ON la.apartment_ID = a.apartment_ID
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE la.end_date IS NOT NULL
    """ + (" AND l.city = ?" if city else "")
    params = (city,) if city else None
    row = execute_query(query, params, fetch_one=True) or {}
    raw = row.get("max_date")
    if not raw:
        return None
    try:
        return _datetime.strptime(str(raw), "%Y-%m-%d").date()
    except Exception:
        return None


def get_lease_date_range(location=None, grouping="month"):
    """Return default start/end dates for lease-based timeseries."""
    grouping_norm = (grouping or "").strip().lower()
    grouping_norm = "year" if grouping_norm in {"year", "yearly"} else "month"
    earliest = _get_earliest_lease_date(location)
    latest = _get_latest_lease_date(location)
    today = _date.today()
    if not earliest or not latest:
        start = _date(today.year, 1, 1)
        end = today
    else:
        if grouping_norm == "month":
            start = _date(earliest.year, earliest.month, 1)
        else:
            start = _date(earliest.year, 1, 1)
        end = latest
    if start > end:
        start = end
    return {"start_date": start.strftime("%Y-%m-%d"), "end_date": end.strftime("%Y-%m-%d")}


def get_occupancy_timeseries(location=None, start_date=None, end_date=None, grouping="month"):
    """
    Occupancy over time from lease overlaps. Returns series with occupied, vacant, total per period.
    """
    grouping_norm = "year" if (grouping or "").strip().lower() in {"year", "yearly"} else "month"
    start_d = _parse_date(start_date)
    end_d = _parse_date(end_date)
    if end_d is None:
        end_d = _date.today()
    if start_d is None:
        rng = get_lease_date_range(location, grouping_norm)
        start_d = _parse_date(rng.get("start_date")) or _date(end_d.year, 1, 1)
    if start_d > end_d:
        start_d = end_d
    city = _normalize_location(location)
    loc_filter = " AND l.city = ?" if city else ""

    if grouping_norm == "month":
        cursor = _date(start_d.year, start_d.month, 1)
        end_bucket = _date(end_d.year, end_d.month, 1)
        buckets = []
        while cursor <= end_bucket:
            buckets.append(cursor)
            if cursor.month == 12:
                cursor = _date(cursor.year + 1, 1, 1)
            else:
                cursor = _date(cursor.year, cursor.month + 1, 1)
    else:
        cursor = _date(start_d.year, 1, 1)
        end_bucket = _date(end_d.year, 1, 1)
        buckets = []
        while cursor <= end_bucket:
            buckets.append(cursor)
            cursor = _date(cursor.year + 1, 1, 1)

    total_apartments = get_total_apartments(location or "all")
    series = []
    for bucket in buckets:
        if grouping_norm == "month":
            period_start = bucket
            period_end = _date(bucket.year, bucket.month, _calendar.monthrange(bucket.year, bucket.month)[1])
            period_label = bucket.strftime("%b %Y")
        else:
            period_start = bucket
            period_end = _date(bucket.year, 12, 31)
            period_label = str(bucket.year)
        ps, pe = period_start.isoformat(), period_end.isoformat()
        query = f"""
            SELECT COUNT(DISTINCT la.apartment_ID) AS occupied
            FROM lease_agreements la
            JOIN apartments a ON la.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE date(la.start_date) <= date(?)
              AND date(la.end_date) >= date(?)
              {loc_filter}
        """
        params = [pe, ps]
        if city:
            params.append(city)
        row = execute_query(query, tuple(params), fetch_one=True) or {}
        occupied = int(row.get("occupied") or 0)
        vacant = max(0, total_apartments - occupied)
        series.append({
            "period": period_label,
            "occupied": occupied,
            "vacant": vacant,
            "total": total_apartments,
        })
    return {"start_date": start_d.strftime("%Y-%m-%d"), "end_date": end_d.strftime("%Y-%m-%d"),
            "grouping": grouping_norm, "series": series}


def get_revenue_timeseries(location=None, start_date=None, end_date=None, grouping="month"):
    """
    Revenue over time from lease overlaps. Returns actual_revenue, lost_revenue, potential_revenue per period.
    """
    grouping_norm = "year" if (grouping or "").strip().lower() in {"year", "yearly"} else "month"
    start_d = _parse_date(start_date)
    end_d = _parse_date(end_date)
    if end_d is None:
        end_d = _date.today()
    if start_d is None:
        rng = get_lease_date_range(location, grouping_norm)
        start_d = _parse_date(rng.get("start_date")) or _date(end_d.year, 1, 1)
    if start_d > end_d:
        start_d = end_d
    city = _normalize_location(location)
    loc_filter = " AND l.city = ?" if city else ""
    potential = get_potential_revenue(location or "all")

    if grouping_norm == "month":
        cursor = _date(start_d.year, start_d.month, 1)
        end_bucket = _date(end_d.year, end_d.month, 1)
        buckets = []
        while cursor <= end_bucket:
            buckets.append(cursor)
            if cursor.month == 12:
                cursor = _date(cursor.year + 1, 1, 1)
            else:
                cursor = _date(cursor.year, cursor.month + 1, 1)
    else:
        cursor = _date(start_d.year, 1, 1)
        end_bucket = _date(end_d.year, 1, 1)
        buckets = []
        while cursor <= end_bucket:
            buckets.append(cursor)
            cursor = _date(cursor.year + 1, 1, 1)

    series = []
    for bucket in buckets:
        if grouping_norm == "month":
            period_end = _date(bucket.year, bucket.month, _calendar.monthrange(bucket.year, bucket.month)[1])
            period_label = bucket.strftime("%b %Y")
        else:
            period_end = _date(bucket.year, 12, 31)
            period_label = str(bucket.year)
        ps, pe = bucket.isoformat(), period_end.isoformat()
        query = f"""
            SELECT COALESCE(SUM(la.monthly_rent), 0) AS actual
            FROM lease_agreements la
            JOIN apartments a ON la.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE date(la.start_date) <= date(?)
              AND date(la.end_date) >= date(?)
              {loc_filter}
        """
        params = [pe, ps]
        if city:
            params.append(city)
        row = execute_query(query, tuple(params), fetch_one=True) or {}
        actual = float(row.get("actual") or 0)
        lost = max(0.0, potential - actual)
        series.append({
            "period": period_label,
            "actual_revenue": actual,
            "lost_revenue": lost,
            "potential_revenue": potential,
        })
    return {"start_date": start_d.strftime("%Y-%m-%d"), "end_date": end_d.strftime("%Y-%m-%d"),
            "grouping": grouping_norm, "series": series}


def create_occupancy_graph(parent, location=None):
    """
    Create and embed a bar graph of occupied vs total apartments in a tkinter widget.
    Uses shared chart_utils for consistent styling across dashboards.
    """
    occupied_count = get_all_occupancy(location)
    total_count = get_total_apartments(location)
    vacant_count = total_count - occupied_count
    title_location = location if location and str(location).lower() != "all" else "All Locations"
    return create_bar_chart(
        parent,
        labels=["Occupied", "Vacant"],
        values=[occupied_count, vacant_count],
        colors=[ACCENT_GREEN, ACCENT_RED],
        title=f"Apartment Occupancy in {title_location}",
        y_label="Number of Apartments",
        value_formatter="count",
        y_padding=0.5,
    )


def get_monthly_revenue(location=None):
    """
    Calculate total monthly revenue from active leases (actual rent collected).
    Uses lease_agreements for consistency with revenue trend graph.
    
    Args:
        location (str, optional): City name to filter by. None/'all'/'All Locations' = all.
    
    Returns:
        float: Total monthly revenue from active leases
    """
    city = _normalize_location(location)
    loc_filter = " AND l.city = ?" if city else ""
    query = f"""
        SELECT COALESCE(SUM(la.monthly_rent), 0) AS total_revenue
        FROM lease_agreements la
        JOIN apartments a ON la.apartment_ID = a.apartment_ID
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE la.active = 1
        {loc_filter}
    """
    params = (city,) if city else None
    result = execute_query(query, params, fetch_one=True)
    return float(result.get("total_revenue") or 0)


def get_potential_revenue(location=None):
    """
    Calculate potential monthly revenue if all apartments were occupied.
    
    Args:
        location (str, optional): City name to filter by. None/'all'/'All Locations' = all.
    
    Returns:
        float: Potential monthly revenue from all apartments
    """
    city = _normalize_location(location)
    loc_filter = " AND l.city = ?" if city else ""
    query = f"""
        SELECT COALESCE(SUM(a.monthly_rent), 0) AS potential_revenue
        FROM apartments a
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE 1=1
        {loc_filter}
    """
    params = (city,) if city else None
    result = execute_query(query, params, fetch_one=True)
    return float(result.get("potential_revenue") or 0)


def create_performance_graph(parent, location=None):
    """
    Create and embed a bar graph of actual vs potential monthly revenue in a tkinter widget.
    Uses shared chart_utils for consistent styling across dashboards.
    """
    actual_revenue = get_monthly_revenue(location)
    potential_revenue = get_potential_revenue(location)
    lost_revenue = potential_revenue - actual_revenue
    title_location = location if location and str(location).lower() not in {"all", "all locations"} else "All Locations"
    return create_bar_chart(
        parent,
        labels=["Actual Revenue", "Lost Revenue"],
        values=[actual_revenue, lost_revenue],
        colors=[ACCENT_GREEN, ACCENT_ORANGE],
        title=f"Monthly Revenue Performance in {title_location}",
        y_label="Revenue (£)",
        value_formatter="currency",
        y_padding=50,
    )


def create_occupancy_trend_graph(parent, location=None, start_date=None, end_date=None, grouping="month"):
    """Line chart of occupancy over time (Occupied, Vacant). Uses shared chart_utils."""
    data = get_occupancy_timeseries(location=location, start_date=start_date, end_date=end_date, grouping=grouping)
    series_data = data.get("series") or []
    periods = [r.get("period", "") for r in series_data]
    occupied = np.array([float(r.get("occupied") or 0) for r in series_data], dtype=float)
    vacant = np.array([float(r.get("vacant") or 0) for r in series_data], dtype=float)
    title_loc = location if location and str(location).lower() not in {"all", "all locations"} else "All Locations"
    if not series_data:
        return create_trend_chart(parent, periods=[], series=[], title=f"Occupancy Trends - {title_loc}",
                                  y_label="Number of Apartments", y_formatter="count")
    return create_trend_chart(
        parent,
        periods=periods,
        series=[
            ("Occupied", occupied, ACCENT_GREEN),
            ("Vacant", vacant, ACCENT_RED),
        ],
        title=f"Occupancy Trends - {title_loc}",
        y_label="Number of Apartments",
        y_formatter="count",
        fill_primary=True,
        fill_secondary=True,
        primary_color=ACCENT_GREEN,
        kpi_style="text",
        show_kpi=False,
        show_toolbar=True,
        y_lim_dynamic=True,
    )


def create_revenue_trend_graph(parent, location=None, start_date=None, end_date=None, grouping="month"):
    """Line chart of revenue over time (Actual, Lost). Uses shared chart_utils."""
    data = get_revenue_timeseries(location=location, start_date=start_date, end_date=end_date, grouping=grouping)
    series_data = data.get("series") or []
    periods = [r.get("period", "") for r in series_data]
    actual = np.array([float(r.get("actual_revenue") or 0) for r in series_data], dtype=float)
    lost = np.array([float(r.get("lost_revenue") or 0) for r in series_data], dtype=float)
    title_loc = location if location and str(location).lower() not in {"all", "all locations"} else "All Locations"
    if not series_data:
        return create_trend_chart(parent, periods=[], series=[], title=f"Revenue Trends - {title_loc}",
                                  y_label="Revenue (£)", y_formatter="currency")
    return create_trend_chart(
        parent,
        periods=periods,
        series=[
            ("Actual Revenue", actual, ACCENT_GREEN),
            ("Lost Revenue", lost, ACCENT_ORANGE),
        ],
        title=f"Revenue Trends - {title_loc}",
        y_label="Revenue (£)",
        y_formatter="currency",
        fill_primary=True,
        fill_secondary=True,
        primary_color=ACCENT_GREEN,
        kpi_style="text",
        show_kpi=False,
        show_toolbar=True,
        y_lim_dynamic=True,
    )


def generate_performance_report():
     pass
    
def get_all_apartments(location="all"):
    """
    Get all apartments from the database.
    
    Args:
        location (str, optional): City name to filter by. If "All Locations" or None, returns all apartments.
    
    Returns:
        list: List of apartment dictionaries, empty list if error
    """
    if location and location.lower() not in ["all locations", "all"]:
        query = """
            SELECT a.apartment_ID, l.city, a.apartment_address, a.number_of_beds, a.monthly_rent, 
                   CASE WHEN a.occupied = 1 THEN 'Occupied' ELSE 'Vacant' END AS status
            FROM apartments a
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE l.city = ?
            ORDER BY l.city, a.apartment_address
        """
        return execute_query(query, (location,), fetch_all=True)
    else:
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