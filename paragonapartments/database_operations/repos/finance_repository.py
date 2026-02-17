"""
Finance Repository - All finance-related database operations.
Handles invoices, payments, late payment tracking, and financial summaries.
"""

from __future__ import annotations

from database_operations.db_execute import execute_query
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import numpy as np
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


def _setup_graph_cleanup(parent, canvas, fig):
    """
    Set up cleanup for matplotlib canvas to prevent callback errors.
    Mirrors the pattern used in apartment_repository.
    """
    def cleanup(_event=None):
        try:
            canvas.flush_events()
            plt.close(fig)
        except Exception:
            pass

    parent.bind('<Destroy>', cleanup, add='+')


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

    labels = ["Invoiced", "Collected", "Outstanding"]
    values = np.array([total_invoiced, total_collected, outstanding], dtype=float)
    colors = ["#3B8ED0", "#4CAF50", "#FF9800"]  # Blue, Green, Orange

    fig, ax = plt.subplots(figsize=(9, 6))
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    title_location = location if location and str(location).lower() not in {"all", "all locations"} else "All Locations"
    ax.set_title(f"Financial Summary - {title_location}", fontsize=16, fontweight="bold")
    ax.set_ylabel("Amount (£)", fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"£{int(v):,}"))

    # Add value labels
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yval + (max(values) * 0.02 if max(values) > 0 else 1),
            f"£{yval:,.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Late count callout
    ax.text(
        0.99,
        0.95,
        f"Late invoices: {late_count}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85),
    )

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    _setup_graph_cleanup(parent, canvas, fig)
    return canvas


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
    """
    data = get_collected_amount_timeseries(
        location=location,
        start_date=start_date,
        end_date=end_date,
        grouping=grouping,
    )

    series = data.get("series") or []
    periods = [row.get("period") for row in series]
    invoiced_values = np.array([float(row.get("total_invoiced") or 0) for row in series], dtype=float)
    collected_values = np.array([float(row.get("total_collected") or 0) for row in series], dtype=float)
    late_values = np.array([float(row.get("late_count") or 0) for row in series], dtype=float)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax2 = ax.twinx()

    x = np.arange(len(periods))
    # Chart styling inspired by dashboard area-line visuals.
    fig.patch.set_facecolor("#F4F5F7")
    ax.set_facecolor("#F4F5F7")
    ax2.set_facecolor("none")

    # Use visually distinct series colors.
    c_primary = "#14D6C1"     # Invoiced
    c_secondary = "#50545D"   # Payments
    c_tertiary = "#8A8E97"    # Late Invoices

    # Filled primary series (area)
    ax.fill_between(x, invoiced_values, color=c_primary, alpha=0.22, zorder=1)

    # Thicker lines
    inv_line = ax.plot(x, invoiced_values, color=c_primary, linewidth=3.0, alpha=0.98, label="Invoiced", zorder=3)[0]
    col_line = ax.plot(x, collected_values, color=c_secondary, linewidth=2.8, alpha=0.98, label="Payments", zorder=3)[0]
    late_line = ax2.plot(x, late_values, color=c_tertiary, linewidth=2.8, alpha=0.98, label="Late Invoices", zorder=3)[0]

    # Hollow markers with white center
    inv_points = ax.scatter(x, invoiced_values, s=170, facecolors="#F4F5F7", edgecolors=c_primary, linewidths=3.0, zorder=4)
    col_points = ax.scatter(x, collected_values, s=150, facecolors="#F4F5F7", edgecolors=c_secondary, linewidths=2.8, zorder=4)
    late_points = ax2.scatter(x, late_values, s=150, facecolors="#F4F5F7", edgecolors=c_tertiary, linewidths=2.8, zorder=4)

    grouping_norm = str(data.get("grouping") or grouping or "month").lower()
    if grouping_norm == "year":
        tick_rotation = 0
    elif grouping_norm == "month":
        tick_rotation = 0
    else:
        tick_rotation = 22

    ax.set_xticks(x)
    ax.set_xticklabels(periods, rotation=tick_rotation, ha="right" if tick_rotation else "center")
    # Remove side padding so the first/last period sit on the edges.
    ax.margins(x=0)
    ax2.margins(x=0)

    title_location = location if location and str(location).lower() not in {"all", "all locations"} else "All Locations"
    ax.set_title(
        f"Finance Trends - {title_location}",
        fontsize=19,
        fontweight="bold",
        color="#2A2D33",
        y=1.10,  # Keep title clearly at the top of the chart area
    )
    ax.set_ylabel("Amount (£)", fontsize=13, color="#4C5057")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"£{int(v):,}"))
    # Keep secondary axis for plotting late series, but hide its numeric scale
    # to avoid confusion with weekly numbers on the chart edge.
    ax2.set_ylabel("")

    # Use dynamic lower bounds (non-zero aware) so the chart does not
    # unnecessarily start at 0 when meaningful values are above zero.
    amount_all = np.concatenate([invoiced_values, collected_values])
    amount_non_zero = amount_all[amount_all > 0]
    if amount_non_zero.size > 0:
        amount_min = float(np.min(amount_non_zero))
        amount_max = float(np.max(amount_all))
        span = max(1.0, amount_max - amount_min)
        lower = max(0.0, amount_min - span * 0.20)
        upper = amount_max + span * 0.15
        ax.set_ylim(lower, upper)

    late_non_zero = late_values[late_values > 0]
    if late_non_zero.size > 0:
        late_min = float(np.min(late_non_zero))
        late_max = float(np.max(late_values))
        l_span = max(1.0, late_max - late_min)
        l_lower = max(0.0, late_min - l_span * 0.30)
        l_upper = late_max + l_span * 0.20
        ax2.set_ylim(l_lower, l_upper)
    # Graph-paper style background grid pattern.
    ax.grid(True, axis="y", color="#D5D7DC", alpha=0.9, linewidth=1)
    ax.grid(True, axis="x", color="#DFE2E8", alpha=0.75, linewidth=0.9)

    # Subtle spine styling (left/bottom only)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
        ax2.spines[s].set_visible(False)
    ax.spines["left"].set_color("#555A63")
    ax.spines["bottom"].set_color("#555A63")
    ax.spines["left"].set_linewidth(1.8)
    ax.spines["bottom"].set_linewidth(1.8)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", colors="#434852", labelsize=12)
    ax.tick_params(axis="y", colors="#434852", labelsize=12)
    ax2.tick_params(axis="y", which="both", right=False, labelright=False)
    # Bold month/year x-axis labels and both y-axis number scales
    for lbl in ax.get_xticklabels():
        lbl.set_fontweight("bold")
    for lbl in ax.get_yticklabels():
        lbl.set_fontweight("bold")
    # Secondary-axis labels are hidden intentionally.

    # Add minor grid for subtle background pattern.
    ax.minorticks_on()
    ax.grid(True, which="minor", axis="both", color="#ECEEF2", alpha=0.7, linewidth=0.6)

    # Combined legend placed outside the plot (top-left).
    handles = [inv_line, col_line, late_line]
    labels = [h.get_label() for h in handles]
    ax.legend(
        handles,
        labels,
        loc="lower left",
        bbox_to_anchor=(0.0, 1.02),
        ncol=3,
        borderaxespad=0.0,
        framealpha=0.95,
        facecolor="white",
        edgecolor="#D0D2D8",
        fontsize=12,
    )

    # Reserve right margin for KPI badges
    # Default subplot layout (matches desired subplot configuration).
    fig.subplots_adjust(left=0.088, bottom=0.117, right=0.87, top=0.836, wspace=0.2, hspace=0.2)

    def _pct_change(vals: np.ndarray) -> float:
        if len(vals) < 2:
            return 0.0
        first = float(vals[0])
        last = float(vals[-1])
        if abs(first) < 1e-9:
            return 0.0
        return ((last - first) / abs(first)) * 100.0

    kpis = [
        ("Invoiced", _pct_change(invoiced_values), c_primary),
        ("Payments", _pct_change(collected_values), c_secondary),
        ("Late", _pct_change(late_values), c_tertiary),
    ]

    # Right-side circular KPI badges (visual cue like provided reference).
    y_slots = [0.66, 0.48, 0.30]
    for (name, pct, color), y_pos in zip(kpis, y_slots):
        sign = "+" if pct >= 0 else ""
        fig.text(
            0.94,
            y_pos,
            f"{sign}{pct:.2f}%",
            ha="center",
            va="center",
            fontsize=12,
            color="white",
            bbox=dict(boxstyle="circle,pad=0.52", fc=color, ec="#D9DBE0", lw=8, alpha=0.98),
        )
        fig.text(
            0.94,
            y_pos - 0.06,
            name,
            ha="center",
            va="center",
            fontsize=9,
            color="#5A5F69",
        )

    # Hover tooltip for exact period/value inspection.
    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(12, 12),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.35", fc="white", alpha=0.9),
        arrowprops=dict(arrowstyle="->"),
        fontsize=11,
    )
    annot.set_visible(False)
    annot2 = ax2.annotate(
        "",
        xy=(0, 0),
        xytext=(12, 12),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.35", fc="white", alpha=0.9),
        arrowprops=dict(arrowstyle="->"),
        fontsize=11,
    )
    annot2.set_visible(False)

    def _update_annot(ind, series_label: str, value_fmt: str, target_annot):
        idx = int(ind["ind"][0])
        x_val = x[idx]
        if series_label == "Invoiced":
            y_val = invoiced_values[idx]
        elif series_label == "Payments":
            y_val = collected_values[idx]
        else:
            y_val = late_values[idx]
        target_annot.xy = (x_val, y_val)
        if value_fmt == "currency":
            value_text = f"£{y_val:,.2f}"
        else:
            value_text = f"{int(y_val)}"
        target_annot.set_text(f"{periods[idx]}\n{series_label}: {value_text}")

    def _on_move(event):
        if event.inaxes not in (ax, ax2):
            changed = False
            if annot.get_visible():
                annot.set_visible(False)
                changed = True
            if annot2.get_visible():
                annot2.set_visible(False)
                changed = True
            if changed:
                canvas.draw_idle()
            return

        hit = False
        hit_late = False
        contains_inv, ind_inv = inv_points.contains(event)
        if contains_inv:
            _update_annot(ind_inv, "Invoiced", "currency", annot)
            annot2.set_visible(False)
            hit = True
        else:
            contains_col, ind_col = col_points.contains(event)
            if contains_col:
                _update_annot(ind_col, "Payments", "currency", annot)
                annot2.set_visible(False)
                hit = True
            else:
                contains_late, ind_late = late_points.contains(event)
                if contains_late:
                    _update_annot(ind_late, "Late Invoices", "count", annot2)
                    annot.set_visible(False)
                    hit = True
                    hit_late = True

        if hit:
            if hit_late:
                annot2.set_visible(True)
            else:
                annot.set_visible(True)
            canvas.draw_idle()
        else:
            changed = False
            if annot.get_visible():
                annot.set_visible(False)
                changed = True
            if annot2.get_visible():
                annot2.set_visible(False)
                changed = True
            if changed:
                canvas.draw_idle()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.mpl_connect("motion_notify_event", _on_move)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    # Add built-in interactive toolbar (home/back, pan, zoom, save).
    toolbar = NavigationToolbar2Tk(canvas, parent, pack_toolbar=False)
    toolbar.update()
    toolbar.pack(fill="x", padx=20, pady=(0, 10))

    _setup_graph_cleanup(parent, canvas, fig)
    return canvas
