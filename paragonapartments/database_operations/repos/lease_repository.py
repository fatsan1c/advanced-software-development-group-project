import calendar as _calendar
from database_operations.db_execute import execute_query
from database_operations.repos.repo_utils import normalize_location, parse_date
from datetime import date as _date, datetime as _datetime, timedelta as _timedelta
import numpy as np
from database_operations.repos.apartment_repository import get_total_apartments, get_potential_revenue
import pages.components.input_validation as input_validation
from pages.components.chart_utils import (
    ACCENT_GREEN,
    ACCENT_ORANGE,
    ACCENT_RED,
    create_bar_chart,
    create_trend_chart,
)


def get_lease_statistics(location=None):
    """
    Get lease agreement statistics for a location.
    
    Args:
        location (str, optional): City name to filter by. None/'all' for all locations.
    
    Returns:
        dict: {
            'active_leases': int,
            'expiring_soon': int (within 30 days),
            'total_leases': int,
            'expired_leases': int
        }
    """
    city = normalize_location(location)
    loc_filter = " AND l.city = ?" if city else ""
    today = _date.today()
    expiry_threshold = (today + _timedelta(days=30)).isoformat()
    
    # Active leases
    active_query = f"""
        SELECT COUNT(*) AS count
        FROM lease_agreements la
        JOIN apartments a ON la.apartment_ID = a.apartment_ID
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE la.active = 1
          AND date(la.start_date) <= date('now')
          AND date(la.end_date) >= date('now')
        {loc_filter}
    """
    params = (city,) if city else None
    active_result = execute_query(active_query, params, fetch_one=True) or {}
    
    # Expiring soon (active leases ending within 30 days)
    expiring_query = f"""
        SELECT COUNT(*) AS count
        FROM lease_agreements la
        JOIN apartments a ON la.apartment_ID = a.apartment_ID
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE la.active = 1
          AND date(la.start_date) <= date('now')
          AND date(la.end_date) <= date(?)
          AND date(la.end_date) >= date(?)
        {loc_filter}
    """
    exp_params = [expiry_threshold, today.isoformat()]
    if city:
        exp_params.append(city)
    expiring_result = execute_query(expiring_query, tuple(exp_params), fetch_one=True) or {}
    
    # Total leases (all time)
    total_query = f"""
        SELECT COUNT(*) AS count
        FROM lease_agreements la
        JOIN apartments a ON la.apartment_ID = a.apartment_ID
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE 1=1
        {loc_filter}
    """
    total_result = execute_query(total_query, params, fetch_one=True) or {}
    
    # Expired leases (inactive or past end date)
    expired_query = f"""
        SELECT COUNT(*) AS count
        FROM lease_agreements la
        JOIN apartments a ON la.apartment_ID = a.apartment_ID
        JOIN locations l ON a.location_ID = l.location_ID
        WHERE (la.active = 0 OR date(la.end_date) < date('now'))
        {loc_filter}
    """
    expired_result = execute_query(expired_query, params, fetch_one=True) or {}
    
    return {
        "active_leases": int(active_result.get("count") or 0),
        "expiring_soon": int(expiring_result.get("count") or 0),
        "total_leases": int(total_result.get("count") or 0),
        "expired_leases": int(expired_result.get("count") or 0),
    }


def get_lease_trend_timeseries(location=None, start_date=None, end_date=None, grouping="month"):
    """
    Get lease trend data showing new leases, active leases, and expired leases over time.
    
    Args:
        location (str, optional): City name to filter by
        start_date (str, optional): Start date 'YYYY-MM-DD'
        end_date (str, optional): End date 'YYYY-MM-DD'
        grouping (str): 'month' or 'year'
    
    Returns:
        dict: {
            'start_date': str,
            'end_date': str,
            'grouping': str,
            'series': [{
                'period': str,
                'new_leases': int,
                'active_leases': int,
                'expired_leases': int
            }, ...]
        }
    """
    grouping_norm = "year" if (grouping or "").strip().lower() in {"year", "yearly"} else "month"
    start_d = parse_date(start_date)
    end_d = parse_date(end_date)
    
    if end_d is None:
        end_d = _date.today()
    if start_d is None:
        rng = get_lease_date_range(location, grouping_norm)
        start_d = parse_date(rng.get("start_date")) or _date(end_d.year, 1, 1)
    if start_d > end_d:
        start_d = end_d
    
    city = normalize_location(location)
    loc_filter = " AND l.city = ?" if city else ""
    
    # Build time buckets
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
        
        # New leases starting in this period
        new_query = f"""
            SELECT COUNT(*) AS count
            FROM lease_agreements la
            JOIN apartments a ON la.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE date(la.start_date) >= date(?)
              AND date(la.start_date) <= date(?)
              {loc_filter}
        """
        params = [ps, pe]
        if city:
            params.append(city)
        new_result = execute_query(new_query, tuple(params), fetch_one=True) or {}
        
        # Active leases during this period (overlap calculation)
        active_query = f"""
            SELECT COUNT(*) AS count
            FROM lease_agreements la
            JOIN apartments a ON la.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE date(la.start_date) <= date(?)
              AND date(la.end_date) >= date(?)
              {loc_filter}
        """
        active_result = execute_query(active_query, tuple(params), fetch_one=True) or {}
        
        # Expired leases in this period
        expired_query = f"""
            SELECT COUNT(*) AS count
            FROM lease_agreements la
            JOIN apartments a ON la.apartment_ID = a.apartment_ID
            JOIN locations l ON a.location_ID = l.location_ID
            WHERE date(la.end_date) >= date(?)
              AND date(la.end_date) <= date(?)
              AND (la.active = 0 OR date(la.end_date) < date('now'))
              {loc_filter}
        """
        expired_result = execute_query(expired_query, tuple(params), fetch_one=True) or {}
        
        series.append({
            "period": period_label,
            "new_leases": int(new_result.get("count") or 0),
            "active_leases": int(active_result.get("count") or 0),
            "expired_leases": int(expired_result.get("count") or 0),
        })
    
    return {
        "start_date": start_d.strftime("%Y-%m-%d"),
        "end_date": end_d.strftime("%Y-%m-%d"),
        "grouping": grouping_norm,
        "series": series,
    }


def create_lease_trend_graph(parent, location=None, start_date=None, end_date=None, grouping="month"):
    """
    Create and embed a lease trend graph showing new, active, and expired leases over time.
    
    Args:
        parent: Tk/CTk parent widget to embed the graph in
        location (str, optional): City name or None/'all' for all locations
        start_date (str, optional): Start date 'YYYY-MM-DD'
        end_date (str, optional): End date 'YYYY-MM-DD'
        grouping (str): 'month' or 'year'
    
    Returns:
        FigureCanvasTkAgg: embedded canvas
    """
    data = get_lease_trend_timeseries(
        location=location,
        start_date=start_date,
        end_date=end_date,
        grouping=grouping,
    )
    series_data = data.get("series") or []
    periods = [row.get("period") for row in series_data]
    new_values = np.array([int(row.get("new_leases") or 0) for row in series_data], dtype=float)
    active_values = np.array([int(row.get("active_leases") or 0) for row in series_data], dtype=float)
    expired_values = np.array([int(row.get("expired_leases") or 0) for row in series_data], dtype=float)
    print(location)
    title_location = location if location and str(location).lower() not in {"all", "all locations"} else "All Locations"
    return create_trend_chart(
        parent,
        periods=periods,
        series=[
            ("Active Leases", active_values, ACCENT_GREEN),
            ("New Leases", new_values, "#4A90E2"),
        ],
        title=f"Lease Trends - {title_location}",
        y_label="Number of Leases",
        y_formatter="number",
        fill_primary=True,
        fill_secondary=False,
        primary_color=ACCENT_GREEN,
        secondary_axis=("Expired", expired_values, ACCENT_ORANGE),
        show_kpi=False,
        show_toolbar=True,
        y_lim_dynamic=True,
    )


def _get_earliest_lease_date(location=None):
    """Earliest lease start_date for location."""
    city = normalize_location(location)
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
    city = normalize_location(location)
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
    start_d = parse_date(start_date)
    end_d = parse_date(end_date)
    if end_d is None:
        end_d = _date.today()
    if start_d is None:
        rng = get_lease_date_range(location, grouping_norm)
        start_d = parse_date(rng.get("start_date")) or _date(end_d.year, 1, 1)
    if start_d > end_d:
        start_d = end_d
    city = normalize_location(location)
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
    start_d = parse_date(start_date)
    end_d = parse_date(end_date)
    if end_d is None:
        end_d = _date.today()
    if start_d is None:
        rng = get_lease_date_range(location, grouping_norm)
        start_d = parse_date(rng.get("start_date")) or _date(end_d.year, 1, 1)
    if start_d > end_d:
        start_d = end_d
    city = normalize_location(location)
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
