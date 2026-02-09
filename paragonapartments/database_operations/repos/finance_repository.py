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
import numpy as np


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
