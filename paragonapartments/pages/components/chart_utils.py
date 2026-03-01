"""
Shared chart utilities for Paragon Apartments.
Provides reusable bar and trend chart builders used by Finance, Manager, and other dashboards.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from datetime import date as _date

try:
    from scipy.interpolate import PchipInterpolator
    _HAS_PCHIP = True
except ImportError:
    _HAS_PCHIP = False

# Shared styling constants - clean, professional palette
GRAPH_BG = "#F8F9FA"
GRAPH_TITLE_COLOR = "#1A1D24"
GRAPH_LABEL_COLOR = "#4A4F5C"
ACCENT_GREEN = "#2BA89A"
ACCENT_RED = "#C75B6D"
ACCENT_ORANGE = "#D4955A"
ACCENT_BLUE = "#5B9FD4"  # Soft blue for neutral/primary metrics (e.g. Invoiced)
GRID_Y_COLOR = "#E2E5E9"
GRID_X_COLOR = "#E8EAED"
SPINE_COLOR = "#A8ADB8"
TICK_COLOR = "#5A5F6B"
LEGEND_EDGE = "#D0D4DA"
BAR_EDGE = "#FFFFFF"


def setup_graph_cleanup(parent, canvas, fig):
    """Set up cleanup for matplotlib canvas to prevent callback errors when parent is destroyed."""
    def cleanup(_event=None):
        try:
            canvas.flush_events()
            plt.close(fig)
        except Exception:
            pass
    parent.bind("<Destroy>", cleanup, add="+")


def _pct_change(vals: np.ndarray) -> float:
    """Compute percentage change from first to last value."""
    if len(vals) < 2:
        return 0.0
    first, last = float(vals[0]), float(vals[-1])
    if abs(first) < 1e-9:
        return 0.0
    return ((last - first) / abs(first)) * 100.0


def _throttle_xticks(periods: list, max_labels: int = 12):
    """Return (tick_indices, tick_labels, rotation, ha, bottom_margin)."""
    n = len(periods)
    if n >= max_labels:
        step = max(1, n // max_labels)
        indices = list(range(0, n, step))
        if indices[-1] != n - 1:
            indices.append(n - 1)
        return indices, [periods[i] for i in indices], 45, "right", 0.18
    return list(range(n)), periods, 45 if n > 6 else 0, "right" if n > 6 else "center", 0.18 if n > 6 else 0.117


def _find_today_position(periods: list[str]) -> int | None:
    """
    Find the position in periods list that corresponds to today's date.
    Handles formats like "Jan 2024" (monthly) or "2024" (yearly).
    Returns None if today is not found in the periods.
    """
    today = _date.today()
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    
    for i, period in enumerate(periods):
        period_lower = period.lower().strip()
        parts = period_lower.split()
        
        try:
            # Yearly format: "2024"
            if len(parts) == 1 and parts[0].isdigit():
                year = int(parts[0])
                if year == today.year:
                    return i
            
            # Monthly format: "Jan 2024", "January 2024"
            elif len(parts) == 2:
                month_str = parts[0][:3]  # Take first 3 chars for month
                year = int(parts[1])
                if month_str in month_map:
                    month = month_map[month_str]
                    if year == today.year and month == today.month:
                        return i
        except (ValueError, IndexError):
            continue
    
    return None


def create_bar_chart(
    parent,
    labels: list[str],
    values: list[float],
    colors: list[str],
    title: str,
    y_label: str,
    *,
    value_formatter: str = "count",
    x_positions: list[float] | None = None,
    overlay_text: str | None = None,
    y_padding: float | None = None,
    bar_label_fontsize: int = 15,
) -> FigureCanvasTkAgg:
    """
    Create and embed a bar chart (e.g. summary, occupancy, performance).

    Args:
        parent: Tk/CTk parent widget
        labels: Bar labels
        values: Bar values
        colors: Bar colors
        title: Chart title
        y_label: Y-axis label
        value_formatter: "count" (integers), "currency" (£1,234), or "currency_decimal" (£1,234.56)
        x_positions: Optional custom x positions (default: 0.35, 0.65 for 2 bars)
        overlay_text: Optional text overlay (e.g. "Late invoices: 5")
        y_padding: Optional padding for value labels above bars

    Returns:
        FigureCanvasTkAgg canvas
    """
    values_arr = np.array(values, dtype=float)
    n = len(labels)
    x_pos = x_positions if x_positions is not None else (
        [0.35, 0.65] if n == 2 else np.arange(n)
    )
    width = 0.25 if n <= 2 else 0.6
    x_lim = (-0.1, 1.1) if n <= 2 else (-0.5, n - 0.5)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor(GRAPH_BG)
    ax.set_facecolor(GRAPH_BG)

    bars = ax.bar(
        x_pos, values_arr, color=colors, width=width,
        edgecolor=BAR_EDGE, linewidth=1.2,
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_xlim(x_lim)

    pad = y_padding
    if pad is None:
        pad = max(values_arr) * 0.02 if values_arr.size and max(values_arr) > 0 else 1

    for bar in bars:
        yval = bar.get_height()
        if value_formatter == "currency":
            txt = f"£{int(yval):,}"
        elif value_formatter == "currency_decimal":
            txt = f"£{yval:,.2f}"
        else:
            txt = str(int(yval))
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yval + pad,
            txt,
            ha="center",
            va="bottom",
            fontsize=bar_label_fontsize,
            fontweight="600",
            color=GRAPH_TITLE_COLOR,
        )

    ax.set_title(title, fontsize=20, fontweight="600", color=GRAPH_TITLE_COLOR, y=1.08)
    ax.set_ylabel(y_label, fontsize=14, color=GRAPH_LABEL_COLOR)
    ax.set_ylim(0, max(values_arr) + (pad * 5) if values_arr.size else 10)

    if value_formatter in ("currency", "currency_decimal"):
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"£{int(v):,}"))

    if overlay_text:
        ax.text(
            0.99, 0.95, overlay_text,
            transform=ax.transAxes, ha="right", va="top", fontsize=11, fontweight="600",
            color=GRAPH_LABEL_COLOR,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=LEGEND_EDGE, alpha=0.95),
        )

    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(SPINE_COLOR)
    ax.spines["bottom"].set_color(SPINE_COLOR)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)
    ax.tick_params(axis="both", colors=TICK_COLOR, labelsize=13)
    for lbl in ax.get_xticklabels():
        lbl.set_fontweight("bold")
    for lbl in ax.get_yticklabels():
        lbl.set_fontweight("bold")
    fig.subplots_adjust(left=0.12, bottom=0.12, right=0.95, top=0.88)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
    setup_graph_cleanup(parent, canvas, fig)
    return canvas


def create_trend_chart(
    parent,
    periods: list[str],
    series: list[tuple[str, np.ndarray, str]],
    title: str,
    y_label: str,
    *,
    y_formatter: str = "currency",
    fill_primary: bool = True,
    fill_secondary: bool = False,
    primary_color: str | None = None,
    secondary_axis: tuple[str, np.ndarray, str] | None = None,
    kpi_style: str = "text",
    show_kpi: bool = True,
    show_toolbar: bool = True,
    y_lim_dynamic: bool = False,
    show_today_marker: bool = True,
) -> FigureCanvasTkAgg:
    """
    Create and embed a multi-series trend line chart with grid, legend, KPI badges, toolbar.

    Args:
        parent: Tk/CTk parent widget
        periods: X-axis period labels
        series: List of (name, values_array, color) for primary axis
        title: Chart title
        y_label: Y-axis label
        y_formatter: "currency" or "count"
        fill_primary: Fill area under first series
        fill_secondary: Also fill area under second series (e.g. Payments)
        primary_color: Color for fill (default: first series color)
        secondary_axis: Optional (name, values, color) for twin axis
        kpi_style: "text" (simple) or "circle" (finance-style badges)
        show_kpi: Show percentage change badges on the right
        show_toolbar: Add NavigationToolbar2Tk
        y_lim_dynamic: Use dynamic y-limits (non-zero aware) for primary axis
        show_today_marker: Show vertical line marking today's date

    Returns:
        FigureCanvasTkAgg canvas
    """
    if not series:
        fig, ax = plt.subplots(figsize=(11, 6.5))
        fig.patch.set_facecolor(GRAPH_BG)
        ax.set_facecolor(GRAPH_BG)
        ax.set_title(title or "No data for the selected period", fontsize=16, color=GRAPH_TITLE_COLOR)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
        setup_graph_cleanup(parent, canvas, fig)
        return canvas

    use_twin = secondary_axis is not None
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax2 = ax.twinx() if use_twin else None

    fig.patch.set_facecolor(GRAPH_BG)
    ax.set_facecolor(GRAPH_BG)
    if ax2:
        ax2.set_facecolor("none")

    x = np.arange(len(periods))
    tick_indices, tick_labels, tick_rot, tick_ha, bottom_margin = _throttle_xticks(periods)
    n_periods = len(periods)
    # Match finance: only show scatter markers at tick positions when many periods (avoids cluttered checkpoints)
    max_markers = 12
    scatter_indices = tick_indices if n_periods > max_markers else list(range(n_periods))

    def _smooth_series(x_orig, vals):
        """PCHIP interpolation: smooth transitions, no overshoot (monotone)."""
        n = len(vals)
        if n < 3 or not _HAS_PCHIP:
            return x_orig, vals
        pchip = PchipInterpolator(x_orig, vals)
        x_smooth = np.linspace(0, n - 1, max(n * 3, 36))
        y_smooth = np.clip(pchip(x_smooth), 0, np.max(vals))
        return x_smooth, y_smooth

    # Primary series - area fills (smoothed for gentler transitions)
    first_name, first_vals, first_color = series[0]
    fill_color = primary_color or first_color
    if fill_primary:
        x_f, y_f = _smooth_series(x, first_vals)
        ax.fill_between(x_f, y_f, alpha=0.38, color=fill_color, zorder=1)
    # Second primary series
    if fill_secondary and len(series) >= 2:
        _, second_vals, second_color = series[1]
        x_s, y_s = _smooth_series(x, second_vals)
        ax.fill_between(x_s, y_s, alpha=0.22, color=second_color, zorder=2)

    lines = []
    scatters = []
    for i, (name, vals, color) in enumerate(series):
        lw = 2.5 if i == 0 else 2.2
        x_plot, y_plot = _smooth_series(x, vals)
        line = ax.plot(x_plot, y_plot, color=color, linewidth=lw, alpha=0.95, label=name, zorder=3)[0]
        lines.append(line)
        sx, sv = x[scatter_indices], vals[scatter_indices]
        s = ax.scatter(sx, sv, s=70 if i == 0 else 55, facecolors=GRAPH_BG, edgecolors=color, linewidths=2, zorder=4)
        scatters.append(s)

    # Secondary axis (smoothed)
    if use_twin:
        sec_name, sec_vals, sec_color = secondary_axis
        x_sec, y_sec = _smooth_series(x, sec_vals)
        line2 = ax2.plot(x_sec, y_sec, color=sec_color, linewidth=2.2, alpha=0.95, label=sec_name, zorder=3)[0]
        lines.append(line2)
        s2 = ax2.scatter(x[scatter_indices], sec_vals[scatter_indices], s=55, facecolors=GRAPH_BG, edgecolors=sec_color, linewidths=2, zorder=4)
        scatters.append(s2)

    ax.set_xticks(x[tick_indices])
    ax.set_xticklabels(tick_labels, rotation=tick_rot, ha=tick_ha, fontsize=10)
    ax.margins(x=0)
    if ax2:
        ax2.margins(x=0)

    ax.set_title(title, fontsize=20, fontweight="600", color=GRAPH_TITLE_COLOR, y=1.10)
    ax.set_ylabel(y_label, fontsize=14, color=GRAPH_LABEL_COLOR)
    if y_formatter == "currency":
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"£{int(v):,}"))
    if ax2:
        ax2.set_ylabel("")
        ax2.tick_params(axis="y", which="both", right=False, labelright=False)

    # Y limits - data-aware padding so small values (e.g. occupancy 5–20) don't show 0–1000
    all_primary = np.concatenate([v for _, v, _ in series])
    if y_lim_dynamic and all_primary.size > 0:
        non_zero = all_primary[all_primary > 0]
        if non_zero.size > 0:
            mn, mx = float(np.min(non_zero)), float(np.max(all_primary))
            span = max(1.0, mx - mn)
            ax.set_ylim(max(0, mn - span * 0.20), mx + span * 0.15)
        else:
            mx = float(np.max(all_primary))
            pad = max(1, mx * 0.15) if y_formatter == "count" else max(100, mx * 0.10)
            ax.set_ylim(0, mx + pad)
    else:
        if all_primary.size > 0:
            mx = float(np.max(all_primary))
            pad = max(1, mx * 0.15) if y_formatter == "count" else max(100, mx * 0.10)
            ax.set_ylim(0, mx + pad)
        else:
            ax.set_ylim(0, 10)

    if use_twin:
        sec_vals = secondary_axis[1]
        sec_non_zero = sec_vals[sec_vals > 0]
        if sec_non_zero.size > 0:
            smn, smx = float(np.min(sec_non_zero)), float(np.max(sec_vals))
            sspan = max(1.0, smx - smn)
            ax2.set_ylim(max(0, smn - sspan * 0.30), smx + sspan * 0.20)

    # Minimal grid - subtle, professional
    ax.grid(True, axis="y", color=GRID_Y_COLOR, alpha=0.55, linewidth=0.9)
    ax.grid(True, axis="x", color=GRID_X_COLOR, alpha=0.4, linewidth=0.65)

    # Today marker - vertical line at current date position
    if show_today_marker:
        today_pos = _find_today_position(periods)
        if today_pos is not None:
            y_min, y_max = ax.get_ylim()
            # Draw line from bottom to 92% of height (leave room for label at top)
            ax.plot([today_pos, today_pos], [y_min, y_max * 0.92], 
                   color="#E74C3C", linestyle="--", linewidth=2, alpha=0.7, zorder=5)
            # Add "Today" label at the top
            ax.text(
                today_pos, y_max * 0.96, "Today",
                ha="center", va="center", fontsize=10, fontweight="bold",
                color="#E74C3C",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#E74C3C", alpha=0.95, linewidth=1.5),
                zorder=6
            )

    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
        if ax2:
            ax2.spines[s].set_visible(False)
    ax.spines["left"].set_color(SPINE_COLOR)
    ax.spines["bottom"].set_color(SPINE_COLOR)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)
    if ax2:
        ax2.spines["left"].set_visible(False)
        ax2.spines["bottom"].set_visible(False)
    ax.tick_params(axis="both", colors=TICK_COLOR, labelsize=13)
    for lbl in ax.get_xticklabels():
        lbl.set_fontweight("bold")
    for lbl in ax.get_yticklabels():
        lbl.set_fontweight("bold")

    handles = lines
    ax.legend(
        handles, [h.get_label() for h in handles],
        loc="lower left", bbox_to_anchor=(0.0, 1.02),
        ncol=len(handles), framealpha=0.98, facecolor="white", edgecolor=LEGEND_EDGE,
        prop={"size": 12, "weight": "500"},
    )

    right_margin = 0.87 if show_kpi else 0.95
    fig.subplots_adjust(left=0.088, bottom=bottom_margin, right=right_margin, top=0.836)

    # KPI badges (right side)
    if show_kpi:
        kpi_series = list(series)
        if use_twin:
            kpi_series.append(secondary_axis)
        y_slots = [0.66 - i * 0.18 for i in range(len(kpi_series))]
        for (name, vals, color), y_pos in zip(kpi_series, y_slots):
            pct = _pct_change(vals)
            sign = "+" if pct >= 0 else ""
            if kpi_style == "circle":
                fig.text(0.94, y_pos, f"{sign}{pct:.2f}%", ha="center", va="center", fontsize=12,
                         color="white", bbox=dict(boxstyle="circle,pad=0.52", fc=color, ec="#D9DBE0", lw=8, alpha=0.98))
                fig.text(0.94, y_pos - 0.06, name, ha="center", va="center", fontsize=9, color="#5A5F69")
            else:
                fig.text(0.94, y_pos, f"{sign}{pct:.2f}%", ha="center", va="center", fontsize=12, fontweight="bold", color=color)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
    if show_toolbar:
        toolbar = NavigationToolbar2Tk(canvas, parent, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(fill="x", padx=20, pady=(0, 10))
    setup_graph_cleanup(parent, canvas, fig)
    return canvas
