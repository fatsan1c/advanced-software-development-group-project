"""
Finance Repository - All finance-related database operations.
Handles invoices, payments, late payment tracking, and financial summaries.
"""

from __future__ import annotations

from database_operations.db_execute import execute_query
import numpy as np
from pages.components.chart_utils import create_bar_chart, create_trend_chart, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_BLUE
from datetime import date as _date, datetime as _datetime, timedelta as _timedelta


_TENANT_NAME_SELECT_SQL: str | None = None


def _tenant_name_select_sql() -> str:
    """
    Return a SQL snippet selecting a displayable tenant name, compatible with
    both schemas used in this project:
    - tenants(name, ...)
    - tenants(first_name, last_name, ...)
    """
    global _TENANT_NAME_SELECT_SQL
    if _TENANT_NAME_SELECT_SQL is not None:
        return _TENANT_NAME_SELECT_SQL

    cols = execute_query("PRAGMA table_info(tenants)", fetch_all=True) or []
    col_names = {c.get("name") for c in cols}

    if "name" in col_names:
        _TENANT_NAME_SELECT_SQL = "t.name AS tenant_name"
    elif "first_name" in col_names and "last_name" in col_names:
        _TENANT_NAME_SELECT_SQL = "(t.first_name || ' ' || t.last_name) AS tenant_name"
    else:
        # Fallback: always returns something without referencing unknown columns
        _TENANT_NAME_SELECT_SQL = "CAST(t.tenant_ID AS TEXT) AS tenant_name"

    return _TENANT_NAME_SELECT_SQL


def _normalize_location(location: str | None) -> str | None:
    """
    Normalize location input used across the app.

    Accepts None, 'all', 'All Locations', etc. Returns:
    - None when no filtering should be applied
    - city string when filtering by a specific city
    """
    if not location:
        return None
    loc = str(location).strip()
    if not loc:
        return None
    if loc.lower() in {"all", "all locations", "alllocation", "alllocations"}:
        return None
    return loc


def _invoice_base_join_sql() -> str:
    """
    Shared join for invoice/location enrichment.
    Uses ACTIVE lease_agreements to infer tenant's current apartment/location.
    """
    return """
        FROM invoices i
        JOIN tenants t ON i.tenant_ID = t.tenant_ID
        LEFT JOIN lease_agreements la
               ON la.tenant_ID = t.tenant_ID AND la.active = 1
        LEFT JOIN apartments a ON la.apartment_ID = a.apartment_ID
        LEFT JOIN locations l ON a.location_ID = l.location_ID
    """


def _payment_base_join_sql() -> str:
    """
    Shared join for payment/location enrichment.
    """
    return """
        FROM payments p
        JOIN tenants t ON p.tenant_ID = t.tenant_ID
        LEFT JOIN lease_agreements la
               ON la.tenant_ID = t.tenant_ID AND la.active = 1
        LEFT JOIN apartments a ON la.apartment_ID = a.apartment_ID
        LEFT JOIN locations l ON a.location_ID = l.location_ID
        LEFT JOIN invoices i ON p.invoice_ID = i.invoice_ID
    """


def get_invoices(location: str | None = None, paid: int | None = None):
    """
    Get invoices enriched with tenant name and city.

    Args:
        location (str, optional): City name to filter by, or None/"all" for all locations.
        paid (int, optional): 0 for unpaid, 1 for paid, None for all.

    Returns:
        list: List of invoice dictionaries.
    """
    city = _normalize_location(location)

    query = f"""
        SELECT
            i.invoice_ID,
            i.tenant_ID,
            {_tenant_name_select_sql()},
            l.city,
            i.amount_due,
            i.due_date,
            i.issue_date,
            i.paid
        {_invoice_base_join_sql()}
        WHERE 1=1
          {"AND l.city = ?" if city else ""}
          {"AND i.paid = ?" if paid in (0, 1) else ""}
        ORDER BY date(i.due_date) DESC, i.invoice_ID DESC
    """

    params = []
    if city:
        params.append(city)
    if paid in (0, 1):
        params.append(int(paid))
    return execute_query(query, tuple(params), fetch_all=True)


def get_late_invoices(location: str | None = None, as_of: str | None = None):
    """
    Get unpaid invoices whose due_date is before the given date (or today).

    Args:
        location (str, optional): City name to filter by, or None/"all" for all locations.
        as_of (str, optional): Date string 'YYYY-MM-DD'. Defaults to SQLite 'now' date.

    Returns:
        list: List of late invoice dictionaries.
    """
    city = _normalize_location(location)
    as_of_expr = "date(?)" if as_of else "date('now')"

    query = f"""
        SELECT
            i.invoice_ID,
            i.tenant_ID,
            {_tenant_name_select_sql()},
            l.city,
            i.amount_due,
            i.due_date,
            i.issue_date,
            i.paid
        {_invoice_base_join_sql()}
        WHERE i.paid = 0
          AND date(i.due_date) < {as_of_expr}
          {"AND l.city = ?" if city else ""}
        ORDER BY date(i.due_date) ASC, i.invoice_ID ASC
    """

    params = []
    if as_of:
        params.append(as_of)
    if city:
        params.append(city)
    return execute_query(query, tuple(params), fetch_all=True)


def create_invoice(tenant_id: int, amount_due: float, due_date: str, issue_date: str | None = None, paid: int = 0):
    """
    Create a new invoice.

    Args:
        tenant_id (int): Tenant ID
        amount_due (float): Amount due
        due_date (str): Due date 'YYYY-MM-DD'
        issue_date (str, optional): Issue date 'YYYY-MM-DD'. Defaults to today.
        paid (int): 0 unpaid, 1 paid

    Returns:
        int: New invoice ID, or None on failure
    """
    issue_date_expr = issue_date if issue_date else None
    query = """
        INSERT INTO invoices (tenant_ID, amount_due, due_date, issue_date, paid)
        VALUES (?, ?, ?, COALESCE(?, date('now')), ?)
    """
    return execute_query(query, (int(tenant_id), float(amount_due), due_date, issue_date_expr, int(paid)), commit=True)


def get_invoice_by_id(invoice_id: int):
    """
    Get a single invoice by ID.

    Returns:
        dict: Invoice row or None
    """
    query = """
        SELECT invoice_ID, tenant_ID, amount_due, due_date, issue_date, paid
        FROM invoices
        WHERE invoice_ID = ?
    """
    return execute_query(query, (int(invoice_id),), fetch_one=True)


def update_invoice(invoice_id: int, **kwargs):
    """
    Update invoice fields.

    Allowed fields: tenant_ID, amount_due, due_date, issue_date, paid

    Returns:
        bool: True if update succeeded, False otherwise.
    """
    allowed_fields = {"tenant_ID", "amount_due", "due_date", "issue_date", "paid"}
    updates = []
    values = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            updates.append(f"{field} = ?")
            values.append(value)

    if not updates:
        return False

    values.append(int(invoice_id))
    query = f"UPDATE invoices SET {', '.join(updates)} WHERE invoice_ID = ?"
    result = execute_query(query, tuple(values), commit=True)
    return result is not None and result > 0


def delete_invoice(invoice_id: int):
    """
    Delete an invoice by ID.

    Returns:
        bool: True if delete succeeded, False otherwise.
    """
    query = "DELETE FROM invoices WHERE invoice_ID = ?"
    result = execute_query(query, (int(invoice_id),), commit=True)
    return result is not None and result > 0


def get_payments(location: str | None = None):
    """
    Get payments enriched with tenant name and city.

    Args:
        location (str, optional): City name to filter by, or None/"all" for all locations.

    Returns:
        list: List of payment dictionaries.
    """
    city = _normalize_location(location)

    query = f"""
        SELECT
            p.payment_ID,
            p.invoice_ID,
            p.tenant_ID,
            {_tenant_name_select_sql()},
            l.city,
            p.payment_date,
            p.amount
        {_payment_base_join_sql()}
        WHERE 1=1
          {"AND l.city = ?" if city else ""}
        ORDER BY date(p.payment_date) DESC, p.payment_ID DESC
    """
    params = (city,) if city else None
    return execute_query(query, params, fetch_all=True)


def record_payment(invoice_id: int, tenant_id: int, amount: float, payment_date: str | None = None, mark_invoice_paid: bool = True):
    """
    Record a payment, optionally marking the invoice as paid.

    Args:
        invoice_id (int): Invoice ID being paid
        tenant_id (int): Tenant ID making the payment
        amount (float): Payment amount
        payment_date (str, optional): 'YYYY-MM-DD'. Defaults to today.
        mark_invoice_paid (bool): If True, set invoices.paid=1 for the given invoice.

    Returns:
        int: New payment ID, or None on failure.
    """
    # Prevent duplicates / inconsistent payments
    inv = execute_query(
        "SELECT invoice_ID, tenant_ID, paid FROM invoices WHERE invoice_ID = ?",
        (int(invoice_id),),
        fetch_one=True
    )
    if not inv:
        raise ValueError(f"Invoice ID {invoice_id} does not exist.")
    if int(inv.get("tenant_ID")) != int(tenant_id):
        raise ValueError(f"Invoice {invoice_id} belongs to tenant ID {inv.get('tenant_ID')}, not {tenant_id}.")
    if int(inv.get("paid") or 0) == 1:
        raise ValueError(f"Invoice {invoice_id} is already marked as paid.")

    existing = execute_query(
        "SELECT payment_ID FROM payments WHERE invoice_ID = ? LIMIT 1",
        (int(invoice_id),),
        fetch_one=True
    )
    if existing:
        raise ValueError(f"A payment has already been recorded for invoice {invoice_id}.")

    payment_date_expr = payment_date if payment_date else None
    insert_query = """
        INSERT INTO payments (invoice_ID, tenant_ID, payment_date, amount)
        VALUES (?, ?, COALESCE(?, date('now')), ?)
    """
    payment_id = execute_query(
        insert_query,
        (int(invoice_id), int(tenant_id), payment_date_expr, float(amount)),
        commit=True
    )

    if payment_id is None:
        return None

    if mark_invoice_paid:
        execute_query(
            "UPDATE invoices SET paid = 1 WHERE invoice_ID = ?",
            (int(invoice_id),),
            commit=True
        )

    return payment_id


def get_financial_summary(location: str | None = None, as_of: str | None = None):
    """
    Get financial totals for invoices/payments, optionally filtered by city.

    Notes:
    - City is inferred from ACTIVE lease agreements.
    - as_of is used for late invoice count; totals are not time-windowed by default.

    Returns:
        dict: {
            'total_invoiced': float,
            'total_collected': float,
            'outstanding': float,
            'late_invoice_count': int
        }
    """
    city = _normalize_location(location)
    as_of_expr = "date(?)" if as_of else "date('now')"

    # Total invoiced
    invoice_query = f"""
        SELECT COALESCE(SUM(i.amount_due), 0) AS total_invoiced
        {_invoice_base_join_sql()}
        WHERE 1=1
          {"AND l.city = ?" if city else ""}
    """
    invoice_params = (city,) if city else None
    inv = execute_query(invoice_query, invoice_params, fetch_one=True) or {}

    # Total collected
    payment_query = f"""
        SELECT COALESCE(SUM(p.amount), 0) AS total_collected
        {_payment_base_join_sql()}
        WHERE 1=1
          {"AND l.city = ?" if city else ""}
    """
    payment_params = (city,) if city else None
    pay = execute_query(payment_query, payment_params, fetch_one=True) or {}

    # Late invoice count
    late_query = f"""
        SELECT COUNT(*) AS late_invoice_count
        {_invoice_base_join_sql()}
        WHERE i.paid = 0
          AND date(i.due_date) < {as_of_expr}
          {"AND l.city = ?" if city else ""}
    """
    late_params = []
    if as_of:
        late_params.append(as_of)
    if city:
        late_params.append(city)
    late = execute_query(late_query, tuple(late_params), fetch_one=True) or {}

    total_invoiced = float(inv.get("total_invoiced") or 0)
    total_collected = float(pay.get("total_collected") or 0)
    outstanding = total_invoiced - total_collected

    return {
        "total_invoiced": total_invoiced,
        "total_collected": total_collected,
        "outstanding": outstanding,
        "late_invoice_count": int(late.get("late_invoice_count") or 0),
    }


def create_financial_summary_graph(parent, location: str | None = None):
    """
    Create and embed a bar chart for invoiced/collected/outstanding for a location.

    Args:
        parent: Tk/CTk parent widget to embed the graph in
        location (str, optional): City name or None/'all' for all locations

    Returns:
        FigureCanvasTkAgg: embedded canvas
    """
    summary = get_financial_summary(location)
    total_invoiced = float(summary.get("total_invoiced", 0) or 0)
    total_collected = float(summary.get("total_collected", 0) or 0)
    outstanding = float(summary.get("outstanding", 0) or 0)
    late_count = int(summary.get("late_invoice_count", 0) or 0)

    title_location = location if location and str(location).lower() not in {"all", "all locations"} else "All Locations"
    return create_bar_chart(
        parent,
        labels=["Invoiced", "Collected", "Outstanding"],
        values=[total_invoiced, total_collected, outstanding],
        colors=[ACCENT_BLUE, ACCENT_GREEN, ACCENT_ORANGE],
        title=f"Financial Summary - {title_location}",
        y_label="Amount (£)",
        value_formatter="currency_decimal",
        overlay_text=f"Late invoices: {late_count}",
        bar_label_fontsize=10,
    )


def _parse_date(date_str: str | None) -> _date | None:
    """
    Parse a date string into a date, or return None for blank.

    Supported formats:
    - DD/MM/YYYY (preferred for UI)
    """
    if date_str is None:
        return None
    s = str(date_str).strip()
    if not s:
        return None
    try:
        parts = s.split("/")
        if len(parts) == 3 and len(parts[0]) == 2:
            return _datetime.strptime(s, "%d/%m/%Y").date()
        raise ValueError("Invalid date pattern")
    except Exception as e:
        raise ValueError(f"Invalid date '{date_str}'. Expected DD/MM/YYYY.") from e


def _month_key(d: _date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def _first_day_months_ago(ref: _date, months_ago: int) -> _date:
    """
    Return the first day of the month N months before ref's month.
    """
    months_ago = int(months_ago)
    total = ref.year * 12 + (ref.month - 1) - months_ago
    year = total // 12
    month = (total % 12) + 1
    return _date(year, month, 1)


def _monday_of_week(d: _date) -> _date:
    """Return Monday of the week containing d."""
    # Python: Monday=0..Sunday=6
    return d - _timedelta(days=d.weekday())


def _ordinal_day(n: int) -> str:
    """Return ordinal string for day number (e.g., 1st, 2nd, 3rd)."""
    if 10 <= (n % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _format_period_label(d: _date, grouping: str) -> str:
    """Format bucket date into a human-friendly label by grouping."""
    if grouping == "week":
        return f"{_ordinal_day(d.day)} {d.strftime('%B')}\n{d.strftime('%Y')}"
    if grouping == "month":
        return f"{d.strftime('%B')}\n{d.strftime('%Y')}"
    return d.strftime("%Y")


def _get_earliest_finance_date(location: str | None = None) -> _date | None:
    """
    Get earliest finance date available for the selected location.

    Checks:
    - payments.payment_date
    - invoices.issue_date
    - invoices.due_date
    """
    city = _normalize_location(location)

    def _fetch_min_date(query: str, params: tuple | None = None) -> _date | None:
        row = execute_query(query, params, fetch_one=True) or {}
        raw = row.get("min_date")
        if not raw:
            return None
        try:
            return _datetime.strptime(str(raw), "%Y-%m-%d").date()
        except Exception:
            return None

    pay_query = f"""
        SELECT MIN(date(p.payment_date)) AS min_date
        {_payment_base_join_sql()}
        WHERE p.payment_date IS NOT NULL
          {"AND l.city = ?" if city else ""}
    """
    inv_issue_query = f"""
        SELECT MIN(date(i.issue_date)) AS min_date
        {_invoice_base_join_sql()}
        WHERE i.issue_date IS NOT NULL
          {"AND l.city = ?" if city else ""}
    """
    inv_due_query = f"""
        SELECT MIN(date(i.due_date)) AS min_date
        {_invoice_base_join_sql()}
        WHERE i.due_date IS NOT NULL
          {"AND l.city = ?" if city else ""}
    """

    params = (city,) if city else None
    candidates = [
        _fetch_min_date(pay_query, params),
        _fetch_min_date(inv_issue_query, params),
        _fetch_min_date(inv_due_query, params),
    ]
    candidates = [d for d in candidates if d is not None]
    return min(candidates) if candidates else None


def _get_latest_finance_date(location: str | None = None) -> _date | None:
    """
    Get latest finance date available for the selected location.

    Checks:
    - payments.payment_date
    - invoices.issue_date
    - invoices.due_date
    """
    city = _normalize_location(location)

    def _fetch_max_date(query: str, params: tuple | None = None) -> _date | None:
        row = execute_query(query, params, fetch_one=True) or {}
        raw = row.get("max_date")
        if not raw:
            return None
        try:
            return _datetime.strptime(str(raw), "%Y-%m-%d").date()
        except Exception:
            return None

    pay_query = f"""
        SELECT MAX(date(p.payment_date)) AS max_date
        {_payment_base_join_sql()}
        WHERE p.payment_date IS NOT NULL
          {"AND l.city = ?" if city else ""}
    """
    inv_issue_query = f"""
        SELECT MAX(date(i.issue_date)) AS max_date
        {_invoice_base_join_sql()}
        WHERE i.issue_date IS NOT NULL
          {"AND l.city = ?" if city else ""}
    """
    inv_due_query = f"""
        SELECT MAX(date(i.due_date)) AS max_date
        {_invoice_base_join_sql()}
        WHERE i.due_date IS NOT NULL
          {"AND l.city = ?" if city else ""}
    """

    params = (city,) if city else None
    candidates = [
        _fetch_max_date(pay_query, params),
        _fetch_max_date(inv_issue_query, params),
        _fetch_max_date(inv_due_query, params),
    ]
    candidates = [d for d in candidates if d is not None]
    return max(candidates) if candidates else None


def get_finance_date_range(location: str | None = None, grouping: str = "month") -> dict:
    """
    Return default start/end filter dates based on available finance data.

    - start_date: earliest available bucket start for the selected grouping
    - end_date: latest available finance date
    """
    grouping_norm = (grouping or "").strip().lower()
    if grouping_norm in {"week", "weekly"}:
        grouping_norm = "week"
    elif grouping_norm in {"month", "monthly"}:
        grouping_norm = "month"
    else:
        grouping_norm = "year"

    earliest = _get_earliest_finance_date(location)
    latest = _get_latest_finance_date(location)
    today = _date.today()

    if earliest is None or latest is None:
        # Fallback when no finance data exists yet.
        start = _date(today.year, 1, 1)
        end = today
    else:
        if grouping_norm == "week":
            start = _monday_of_week(earliest)
        elif grouping_norm == "month":
            start = _date(earliest.year, earliest.month, 1)
        else:
            start = _date(earliest.year, 1, 1)
        end = latest

    if start > end:
        start = end

    return {
        "start_date": start.strftime("%d/%m/%Y"),
        "end_date": end.strftime("%d/%m/%Y"),
    }


def _month_keys_between(start: _date, end: _date) -> list[str]:
    """
    Inclusive list of 'YYYY-MM' keys between start and end dates.
    """
    if start > end:
        return []
    y, m = start.year, start.month
    end_y, end_m = end.year, end.month
    keys: list[str] = []
    while (y, m) <= (end_y, end_m):
        keys.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            m = 1
            y += 1
    return keys


def get_collected_amount_timeseries(
    location: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    grouping: str = "month",
) -> dict:
    """
    Get finance timeseries for:
    - invoiced amount
    - collected payment amount
    - late invoice count

    Supported groupings:
    - week / weekly
    - month / monthly
    - year / yearly

    If start_date is not provided, starts from the earliest available finance
    data for the selected location.

    Returns:
        dict: {
          'start_date': 'DD/MM/YYYY',
          'end_date': 'DD/MM/YYYY',
          'grouping': 'week'|'month'|'year',
          'series': [{
              'period': 'DD/MM/YYYY',
              'total_invoiced': float,
              'total_collected': float,
              'late_count': int
          }, ...]
        }
    """
    grouping_norm = (grouping or "").strip().lower()
    if grouping_norm in {"week", "weekly"}:
        grouping_norm = "week"
    elif grouping_norm in {"month", "monthly"}:
        grouping_norm = "month"
    elif grouping_norm in {"year", "yearly"}:
        grouping_norm = "year"
    else:
        raise ValueError("Grouping must be Monthly or Yearly.")

    start_d = _parse_date(start_date)
    auto_start = start_d is None
    end_d = _parse_date(end_date)

    if end_d is None:
        end_d = _date.today()
    if start_d is None:
        earliest = _get_earliest_finance_date(location)
        if earliest:
            if grouping_norm == "week":
                start_d = _monday_of_week(earliest)
            elif grouping_norm == "month":
                start_d = _date(earliest.year, earliest.month, 1)
            else:  # year
                start_d = _date(earliest.year, 1, 1)
        else:
            # Fallback when there is no finance data at all.
            start_d = _date(end_d.year, 1, 1)

    if start_d > end_d:
        raise ValueError("Start date must be on/before end date.")

    city = _normalize_location(location)

    def _period_expr_for(column_sql: str) -> str:
        if grouping_norm == "week":
            # Monday-of-week bucket for the given date column
            return f"date({column_sql}, '-' || ((CAST(strftime('%w', date({column_sql})) AS INTEGER) + 6) % 7) || ' day')"
        if grouping_norm == "month":
            return f"date({column_sql}, 'start of month')"
        return f"date({column_sql}, 'start of year')"

    if grouping_norm == "week":
        pass
    elif grouping_norm == "month":
        pass
    else:  # year
        pass

    # Payments (collected)
    pay_period_expr = _period_expr_for("p.payment_date")
    pay_query = f"""
        SELECT
            {pay_period_expr} AS period_start,
            COALESCE(SUM(p.amount), 0) AS total_collected
        {_payment_base_join_sql()}
        WHERE 1=1
          AND date(p.payment_date) >= date(?)
          AND date(p.payment_date) <= date(?)
          {"AND l.city = ?" if city else ""}
        GROUP BY period_start
        ORDER BY date(period_start) ASC
    """

    params: list = [start_d.isoformat(), end_d.isoformat()]
    if city:
        params.append(city)

    pay_rows = execute_query(pay_query, tuple(params), fetch_all=True) or []
    by_collected: dict[str, float] = {}
    for r in pay_rows:
        k = r.get("period_start")
        if not k:
            continue
        by_collected[str(k)] = float(r.get("total_collected") or 0)

    # Invoices (invoiced amount, bucketed by issue date)
    inv_period_expr = _period_expr_for("i.issue_date")
    inv_query = f"""
        SELECT
            {inv_period_expr} AS period_start,
            COALESCE(SUM(i.amount_due), 0) AS total_invoiced
        {_invoice_base_join_sql()}
        WHERE 1=1
          AND date(i.issue_date) >= date(?)
          AND date(i.issue_date) <= date(?)
          {"AND l.city = ?" if city else ""}
        GROUP BY period_start
        ORDER BY date(period_start) ASC
    """
    inv_rows = execute_query(inv_query, tuple(params), fetch_all=True) or []
    by_invoiced: dict[str, float] = {}
    for r in inv_rows:
        k = r.get("period_start")
        if not k:
            continue
        by_invoiced[str(k)] = float(r.get("total_invoiced") or 0)

    # Late invoices (count, bucketed by due date)
    # Use historical-as-of cutoff so future due dates are not treated as late.
    as_of_cutoff = min(_date.today(), end_d).isoformat()
    late_period_expr = _period_expr_for("i.due_date")
    late_params: list = [start_d.isoformat(), end_d.isoformat(), as_of_cutoff]
    late_query = f"""
        SELECT
            {late_period_expr} AS period_start,
            COUNT(*) AS late_count
        {_invoice_base_join_sql()}
        WHERE i.paid = 0
          AND date(i.due_date) >= date(?)
          AND date(i.due_date) <= date(?)
          AND date(i.due_date) <= date(?)
          {"AND l.city = ?" if city else ""}
        GROUP BY period_start
        ORDER BY date(period_start) ASC
    """
    if city:
        late_params.append(city)
    late_rows = execute_query(late_query, tuple(late_params), fetch_all=True) or []
    by_late_count: dict[str, int] = {}
    for r in late_rows:
        k = r.get("period_start")
        if not k:
            continue
        by_late_count[str(k)] = int(r.get("late_count") or 0)

    # Build continuous buckets and format labels by grouping.
    if grouping_norm == "week":
        cursor = _monday_of_week(start_d)
        end_bucket = _monday_of_week(end_d)
        buckets: list[_date] = []
        while cursor <= end_bucket:
            buckets.append(cursor)
            cursor = cursor + _timedelta(days=7)
    elif grouping_norm == "month":
        cursor = _date(start_d.year, start_d.month, 1)
        end_bucket = _date(end_d.year, end_d.month, 1)
        buckets = []
        y, m = cursor.year, cursor.month
        while (y, m) <= (end_bucket.year, end_bucket.month):
            buckets.append(_date(y, m, 1))
            m += 1
            if m == 13:
                m = 1
                y += 1
    else:  # year
        y = start_d.year
        end_y = end_d.year
        buckets = [_date(year, 1, 1) for year in range(y, end_y + 1)]

    series = []
    for b in buckets:
        iso = b.isoformat()  # 'YYYY-MM-DD' for lookup
        label = _format_period_label(b, grouping_norm)
        series.append(
            {
                "period": label,
                "total_invoiced": float(by_invoiced.get(iso, 0.0)),
                "total_collected": float(by_collected.get(iso, 0.0)),
                "late_count": int(by_late_count.get(iso, 0)),
            }
        )

    # Trim leading/trailing periods where all plotted series are zero.
    # Keep interior zero periods so gaps inside active data remain visible.
    if series:
        def _is_all_zero(row: dict) -> bool:
            return (
                float(row.get("total_invoiced") or 0) == 0.0
                and float(row.get("total_collected") or 0) == 0.0
                and int(row.get("late_count") or 0) == 0
            )

        start_idx = 0
        end_idx = len(series) - 1

        while start_idx <= end_idx and _is_all_zero(series[start_idx]):
            start_idx += 1
        while end_idx >= start_idx and _is_all_zero(series[end_idx]):
            end_idx -= 1

        if start_idx <= end_idx:
            series = series[start_idx:end_idx + 1]
        else:
            # All-zero dataset: keep the first bucket for a stable empty-state chart.
            series = series[:1]

    return {
        "start_date": start_d.strftime("%d/%m/%Y"),
        "end_date": end_d.strftime("%d/%m/%Y"),
        "grouping": grouping_norm,
        "series": series,
    }


def create_collected_trend_graph(
    parent,
    location: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    grouping: str = "month",
):
    """
    Create and embed a multi-series finance trend chart.
    Uses shared chart_utils.create_trend_chart for consistent styling across dashboards.
    """
    data = get_collected_amount_timeseries(
        location=location,
        start_date=start_date,
        end_date=end_date,
        grouping=grouping,
    )
    series_data = data.get("series") or []
    periods = [row.get("period") for row in series_data]
    invoiced_values = np.array([float(row.get("total_invoiced") or 0) for row in series_data], dtype=float)
    collected_values = np.array([float(row.get("total_collected") or 0) for row in series_data], dtype=float)
    late_values = np.array([float(row.get("late_count") or 0) for row in series_data], dtype=float)

    title_location = location if location and str(location).lower() not in {"all", "all locations"} else "All Locations"
    return create_trend_chart(
        parent,
        periods=periods,
        series=[
            ("Invoiced", invoiced_values, ACCENT_GREEN),
            ("Payments", collected_values, "#6B7080"),
        ],
        title=f"Finance Trends - {title_location}",
        y_label="Amount (£)",
        y_formatter="currency",
        fill_primary=True,
        fill_secondary=True,
        primary_color=ACCENT_GREEN,
        secondary_axis=("Late Invoices", late_values, "#8E929C"),
        kpi_style="circle",
        show_toolbar=True,
        y_lim_dynamic=True,
    )
