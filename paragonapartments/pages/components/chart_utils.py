"""Contributors: Aaron Antal-Bento (23013693), Ahmed AlShamy (24045361)

Shared chart utilities for Paragon Apartments.
Provides class-based chart builders used by Finance, Manager, and other dashboards.
"""

from __future__ import annotations

from datetime import date as _date

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from pages.components.config.theme import THEME

_CHART_THEME = THEME.charts
BAR_EDGE = _CHART_THEME.bar_edge
GRAPH_BG = _CHART_THEME.background
GRAPH_LABEL_COLOR = _CHART_THEME.label
GRAPH_TITLE_COLOR = _CHART_THEME.title
GRID_X_COLOR = _CHART_THEME.grid_x
GRID_Y_COLOR = _CHART_THEME.grid_y
KPI_LABEL_COLOR = _CHART_THEME.kpi_label
KPI_RING_COLOR = _CHART_THEME.kpi_ring
LEGEND_EDGE = _CHART_THEME.legend_edge
SPINE_COLOR = _CHART_THEME.spine
TICK_COLOR = _CHART_THEME.tick
TODAY_MARKER_COLOR = _CHART_THEME.today_marker

matplotlib.use("Agg")

try:
    from scipy.interpolate import PchipInterpolator

    _HAS_PCHIP = True
except ImportError:
    _HAS_PCHIP = False


class BaseChart:
    """Shared chart lifecycle helpers."""

    @staticmethod
    def setup_graph_cleanup(parent, canvas, fig):
        """Set up cleanup for matplotlib canvas to prevent callback errors when parent is destroyed."""

        def cleanup(_event=None):
            try:
                canvas.flush_events()
                plt.close(fig)
            except Exception:
                pass

        parent.bind("<Destroy>", cleanup, add="+")

    @staticmethod
    def render_canvas(parent, fig, *, pack_kwargs=None, show_toolbar=False):
        """Render and pack a figure into a tkinter parent."""
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(**(pack_kwargs or {"fill": "both", "expand": True}))
        if show_toolbar:
            toolbar = NavigationToolbar2Tk(canvas, parent, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(fill="x")
        BaseChart.setup_graph_cleanup(parent, canvas, fig)
        return canvas


class BarChart(BaseChart):
    """Builds standard bar charts."""

    @staticmethod
    def create(
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
        """Create and embed a bar chart (e.g. summary, occupancy, performance)."""
        values_arr = np.array(values, dtype=float)
        n = len(labels)
        x_pos = x_positions if x_positions is not None else ([0.35, 0.65] if n == 2 else np.arange(n))
        width = 0.25 if n <= 2 else 0.6
        x_lim = (-0.1, 1.1) if n <= 2 else (-0.5, n - 0.5)

        fig, ax = plt.subplots(figsize=(11, 6.5))
        fig.patch.set_facecolor(GRAPH_BG)
        ax.set_facecolor(GRAPH_BG)

        bars = ax.bar(
            x_pos,
            values_arr,
            color=colors,
            width=width,
            edgecolor=BAR_EDGE,
            linewidth=1.2,
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
                0.99,
                0.95,
                overlay_text,
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=11,
                fontweight="600",
                color=GRAPH_LABEL_COLOR,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=LEGEND_EDGE, alpha=0.95),
            )

        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(SPINE_COLOR)
        ax.spines["bottom"].set_color(SPINE_COLOR)
        ax.spines["left"].set_linewidth(1.5)
        ax.spines["bottom"].set_linewidth(1.5)
        ax.tick_params(axis="both", colors=TICK_COLOR, labelsize=13)
        for label in ax.get_xticklabels():
            label.set_fontweight("bold")
        for label in ax.get_yticklabels():
            label.set_fontweight("bold")
        fig.tight_layout(pad=1.5, rect=[0, 0, 1, 0.96])

        return BarChart.render_canvas(
            parent,
            fig,
            pack_kwargs={"fill": "both", "expand": True, "padx": 20, "pady": 20},
        )


class TrendChart(BaseChart):
    """Builds multi-series trend charts with optional secondary axis and KPI badges."""

    @staticmethod
    def _pct_change(vals: np.ndarray) -> float:
        if len(vals) < 2:
            return 0.0
        first, last = float(vals[0]), float(vals[-1])
        if abs(first) < 1e-9:
            return 0.0
        return ((last - first) / abs(first)) * 100.0

    @staticmethod
    def _throttle_xticks(periods: list, max_labels: int = 12):
        n = len(periods)
        if n >= max_labels:
            step = max(1, n // max_labels)
            indices = list(range(0, n, step))
            if indices[-1] != n - 1:
                indices.append(n - 1)
            return indices, [periods[i] for i in indices], 45, "right", 0.18
        return (
            list(range(n)),
            periods,
            45 if n > 6 else 0,
            "right" if n > 6 else "center",
            0.18 if n > 6 else 0.117,
        )

    @staticmethod
    def _find_today_position(periods: list[str]) -> int | None:
        today = _date.today()
        month_map = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }

        for index, period in enumerate(periods):
            period_lower = period.lower().strip()
            parts = period_lower.split()
            try:
                if len(parts) == 1 and parts[0].isdigit():
                    if int(parts[0]) == today.year:
                        return index
                elif len(parts) == 2:
                    month_str = parts[0][:3]
                    year = int(parts[1])
                    if month_str in month_map and year == today.year and month_map[month_str] == today.month:
                        return index
            except (ValueError, IndexError):
                continue
        return None

    @staticmethod
    def _smooth_series(x_orig, vals):
        """PCHIP interpolation: smooth transitions, no overshoot (monotone)."""
        count = len(vals)
        if count < 3 or not _HAS_PCHIP:
            return x_orig, vals
        pchip = PchipInterpolator(x_orig, vals)
        x_smooth = np.linspace(0, count - 1, max(count * 3, 36))
        y_smooth = np.clip(pchip(x_smooth), 0, np.max(vals))
        return x_smooth, y_smooth

    @staticmethod
    def create(
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
        show_kpi: bool = False,
        show_toolbar: bool = True,
        y_lim_dynamic: bool = False,
        show_today_marker: bool = True,
    ) -> FigureCanvasTkAgg:
        """Create and embed a multi-series trend line chart with grid, legend, and optional KPIs."""
        if not series:
            fig, ax = plt.subplots(figsize=(11, 6.5))
            fig.patch.set_facecolor(GRAPH_BG)
            ax.set_facecolor(GRAPH_BG)
            ax.set_title(title or "No data for the selected period", fontsize=16, color=GRAPH_TITLE_COLOR)
            return TrendChart.render_canvas(
                parent,
                fig,
                pack_kwargs={"fill": "both", "expand": True, "padx": 0, "pady": 0},
            )

        use_twin = secondary_axis is not None
        fig, ax = plt.subplots(figsize=(11, 6.5))
        ax2 = ax.twinx() if use_twin else None

        fig.patch.set_facecolor(GRAPH_BG)
        ax.set_facecolor(GRAPH_BG)
        if ax2:
            ax2.set_facecolor("none")

        x = np.arange(len(periods))
        tick_indices, tick_labels, tick_rot, tick_ha, _ = TrendChart._throttle_xticks(periods)
        n_periods = len(periods)
        max_markers = 12
        scatter_indices = tick_indices if n_periods > max_markers else list(range(n_periods))

        _, first_vals, first_color = series[0]
        fill_color = primary_color or first_color
        if fill_primary:
            x_f, y_f = TrendChart._smooth_series(x, first_vals)
            ax.fill_between(x_f, y_f, alpha=0.38, color=fill_color, zorder=1)
        if fill_secondary and len(series) >= 2:
            _, second_vals, second_color = series[1]
            x_s, y_s = TrendChart._smooth_series(x, second_vals)
            ax.fill_between(x_s, y_s, alpha=0.22, color=second_color, zorder=2)

        lines = []
        for index, (name, vals, color) in enumerate(series):
            lw = 2.5 if index == 0 else 2.2
            x_plot, y_plot = TrendChart._smooth_series(x, vals)
            line = ax.plot(x_plot, y_plot, color=color, linewidth=lw, alpha=0.95, label=name, zorder=3)[0]
            lines.append(line)
            sx, sv = x[scatter_indices], vals[scatter_indices]
            ax.scatter(
                sx,
                sv,
                s=70 if index == 0 else 55,
                facecolors=GRAPH_BG,
                edgecolors=color,
                linewidths=2,
                zorder=4,
            )

        if use_twin and ax2:
            sec_name, sec_vals, sec_color = secondary_axis
            x_sec, y_sec = TrendChart._smooth_series(x, sec_vals)
            line2 = ax2.plot(x_sec, y_sec, color=sec_color, linewidth=2.2, alpha=0.95, label=sec_name, zorder=3)[0]
            lines.append(line2)
            ax2.scatter(
                x[scatter_indices],
                sec_vals[scatter_indices],
                s=55,
                facecolors=GRAPH_BG,
                edgecolors=sec_color,
                linewidths=2,
                zorder=4,
            )

        ax.set_xticks(x[tick_indices])
        ax.set_xticklabels(tick_labels, rotation=tick_rot, ha=tick_ha, fontsize=10)
        ax.margins(x=0)
        if ax2:
            ax2.margins(x=0)

        ax.set_title(title, fontsize=20, fontweight="600", color=GRAPH_TITLE_COLOR, y=1.02)
        ax.set_ylabel(y_label, fontsize=14, color=GRAPH_LABEL_COLOR)
        if y_formatter == "currency":
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"£{int(v):,}"))
        if ax2:
            ax2.set_ylabel("")
            ax2.tick_params(axis="y", which="both", right=False, labelright=False)

        all_primary = np.concatenate([values for _, values, _ in series])
        if y_lim_dynamic and all_primary.size > 0:
            non_zero = all_primary[all_primary > 0]
            if non_zero.size > 0:
                minimum, maximum = float(np.min(non_zero)), float(np.max(all_primary))
                span = max(1.0, maximum - minimum)
                ax.set_ylim(max(0, minimum - span * 0.20), maximum + span * 0.15)
            else:
                maximum = float(np.max(all_primary))
                padding = max(1, maximum * 0.15) if y_formatter == "count" else max(100, maximum * 0.10)
                ax.set_ylim(0, maximum + padding)
        elif all_primary.size > 0:
            maximum = float(np.max(all_primary))
            padding = max(1, maximum * 0.15) if y_formatter == "count" else max(100, maximum * 0.10)
            ax.set_ylim(0, maximum + padding)
        else:
            ax.set_ylim(0, 10)

        if use_twin and ax2:
            sec_vals = secondary_axis[1]
            sec_non_zero = sec_vals[sec_vals > 0]
            if sec_non_zero.size > 0:
                sec_min, sec_max = float(np.min(sec_non_zero)), float(np.max(sec_vals))
                sec_span = max(1.0, sec_max - sec_min)
                ax2.set_ylim(max(0, sec_min - sec_span * 0.30), sec_max + sec_span * 0.20)

        ax.grid(True, axis="y", color=GRID_Y_COLOR, alpha=0.55, linewidth=0.9)
        ax.grid(True, axis="x", color=GRID_X_COLOR, alpha=0.4, linewidth=0.65)

        if show_today_marker:
            today_pos = TrendChart._find_today_position(periods)
            if today_pos is not None:
                y_min, y_max = ax.get_ylim()
                ax.plot(
                    [today_pos, today_pos],
                    [y_min, y_max * 0.92],
                    color=TODAY_MARKER_COLOR,
                    linestyle="--",
                    linewidth=2,
                    alpha=0.7,
                    zorder=5,
                )
                ax.text(
                    today_pos,
                    y_max * 0.96,
                    "Today",
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold",
                    color=TODAY_MARKER_COLOR,
                    bbox=dict(
                        boxstyle="round,pad=0.4",
                        facecolor="white",
                        edgecolor=TODAY_MARKER_COLOR,
                        alpha=0.95,
                        linewidth=1.5,
                    ),
                    zorder=6,
                )

        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
            if ax2:
                ax2.spines[spine].set_visible(False)
        ax.spines["left"].set_color(SPINE_COLOR)
        ax.spines["bottom"].set_color(SPINE_COLOR)
        ax.spines["left"].set_linewidth(1.5)
        ax.spines["bottom"].set_linewidth(1.5)
        if ax2:
            ax2.spines["left"].set_visible(False)
            ax2.spines["bottom"].set_visible(False)
        ax.tick_params(axis="both", colors=TICK_COLOR, labelsize=13)
        for label in ax.get_xticklabels():
            label.set_fontweight("bold")
        for label in ax.get_yticklabels():
            label.set_fontweight("bold")

        ax.legend(
            lines,
            [line.get_label() for line in lines],
            ncol=len(lines),
            framealpha=0.98,
            facecolor="white",
            edgecolor=LEGEND_EDGE,
            prop={"size": 12, "weight": "500"},
        )

        right_margin = 0.87 if show_kpi else 1.0
        fig.tight_layout(pad=1.2, rect=[-0.02, 0, right_margin, 0.98])

        if show_kpi:
            kpi_series = list(series)
            if use_twin and secondary_axis is not None:
                kpi_series.append(secondary_axis)
            y_slots = [0.66 - index * 0.18 for index in range(len(kpi_series))]
            for (name, vals, color), y_pos in zip(kpi_series, y_slots):
                pct = TrendChart._pct_change(vals)
                sign = "+" if pct >= 0 else ""
                if kpi_style == "circle":
                    fig.text(
                        0.94,
                        y_pos,
                        f"{sign}{pct:.2f}%",
                        ha="center",
                        va="center",
                        fontsize=12,
                        color="white",
                        bbox=dict(boxstyle="circle,pad=0.52", fc=color, ec=KPI_RING_COLOR, lw=8, alpha=0.98),
                    )
                    fig.text(0.94, y_pos - 0.06, name, ha="center", va="center", fontsize=9, color=KPI_LABEL_COLOR)
                else:
                    fig.text(
                        0.94,
                        y_pos,
                        f"{sign}{pct:.2f}%",
                        ha="center",
                        va="center",
                        fontsize=12,
                        fontweight="bold",
                        color=color,
                    )

        return TrendChart.render_canvas(
            parent,
            fig,
            pack_kwargs={"fill": "both", "expand": True, "padx": 0, "pady": (10, 0)},
            show_toolbar=show_toolbar,
        )


class PieChart(BaseChart):
    """Builds distribution pie charts."""

    @staticmethod
    def create(
        parent,
        labels: list[str],
        values: list[float],
        colors: list[str],
        title: str,
        *,
        explode: tuple[float, ...] | None = None,
        return_figure: bool = False,
    ) -> FigureCanvasTkAgg | plt.Figure:
        """Create and embed a pie chart showing distribution."""
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor(GRAPH_BG)
        ax.set_facecolor(GRAPH_BG)

        total = sum(values)
        if total == 0:
            ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=14, color=GRAPH_LABEL_COLOR)
            ax.set_title(title, fontsize=16, fontweight="bold", color=GRAPH_TITLE_COLOR, pad=20)
            ax.axis("off")
            if return_figure:
                return fig
            return PieChart.render_canvas(
                parent,
                fig,
                pack_kwargs={"fill": "both", "expand": True, "padx": 20, "pady": 20},
            )

        if explode is None:
            explode = tuple([0.05 if i == 0 else 0 for i in range(len(values))])

        _, _, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            explode=explode,
            textprops={"fontsize": 12, "fontweight": "bold"},
        )

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(14)
            autotext.set_fontweight("bold")

        ax.set_title(title, fontsize=16, fontweight="bold", color=GRAPH_TITLE_COLOR, pad=20)
        ax.axis("equal")

        if return_figure:
            plt.tight_layout()
            return fig

        return PieChart.render_canvas(
            parent,
            fig,
            pack_kwargs={"fill": "both", "expand": True, "padx": 20, "pady": 20},
        )


class ComparisonBarChart(BaseChart):
    """Builds comparison bar charts (e.g., Actual vs Potential vs Lost)."""

    @staticmethod
    def create(
        parent,
        categories: list[str],
        values: list[float],
        colors: list[str],
        title: str,
        y_label: str,
        *,
        value_formatter: str = "currency",
        return_figure: bool = False,
    ) -> FigureCanvasTkAgg | plt.Figure:
        """Create a comparison bar chart."""
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor=BAR_EDGE, linewidth=1.5)

        for bar, value in zip(bars, values):
            height = bar.get_height()
            if value_formatter == "currency":
                txt = f"£{int(value):,}"
            elif value_formatter == "currency_decimal":
                txt = f"£{value:,.2f}"
            else:
                txt = str(int(value))

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                txt,
                ha="center",
                va="bottom",
                fontsize=12,
                fontweight="bold",
                color=GRAPH_TITLE_COLOR,
            )

        ax.set_ylabel(y_label, fontsize=13, fontweight="bold", color=GRAPH_LABEL_COLOR)
        ax.set_title(title, fontsize=16, fontweight="bold", color=GRAPH_TITLE_COLOR, pad=20)

        if value_formatter in ("currency", "currency_decimal"):
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"£{x:,.0f}"))

        ax.grid(False)
        ax.set_axisbelow(True)

        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color(SPINE_COLOR)
        ax.spines["bottom"].set_color(SPINE_COLOR)
        ax.spines["left"].set_linewidth(1.5)
        ax.spines["bottom"].set_linewidth(1.5)
        ax.tick_params(axis="both", colors=TICK_COLOR, labelsize=11)
        for label in ax.get_xticklabels():
            label.set_fontweight("bold")
        for label in ax.get_yticklabels():
            label.set_fontweight("bold")

        if return_figure:
            plt.tight_layout()
            return fig

        return ComparisonBarChart.render_canvas(
            parent,
            fig,
            pack_kwargs={"fill": "both", "expand": True, "padx": 20, "pady": 20},
        )
