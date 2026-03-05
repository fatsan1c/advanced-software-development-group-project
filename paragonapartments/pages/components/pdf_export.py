"""
PDF export utility for charts and reports.

Provides functionality to export matplotlib charts to PDF with optional statistics text.
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import filedialog


def export_chart_to_pdf(
    fig: Figure,
    filename: str | None = None,
    stats_text: str | None = None,
    title: str = "Report",
    save_directory: str | None = None
) -> str | None:
    """
    Export a matplotlib figure to PDF with optional statistics text.
    
    Args:
        fig: Matplotlib Figure object to export
        filename: Optional filename (without extension). If None, uses timestamp
        stats_text: Optional statistics text to include below the chart
        title: Title for the report
        save_directory: Directory to save the PDF. If None, prompts user for location
        
    Returns:
        str: Path to saved PDF file, or None if cancelled
    """
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}"
    
    # Remove .pdf extension if user included it
    if filename.endswith('.pdf'):
        filename = filename[:-4]
    
    # Prompt for save location if not provided
    if save_directory is None:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"{filename}.pdf",
            title="Save Report as PDF"
        )
        
        root.destroy()
        
        if not file_path:
            return None
    else:
        save_path = Path(save_directory)
        save_path.mkdir(parents=True, exist_ok=True)
        file_path = str(save_path / f"{filename}.pdf")
    
    with PdfPages(file_path) as pdf:
        report_fig = _create_report_page(fig, title, stats_text)
        pdf.savefig(report_fig, dpi=300, bbox_inches='tight')
        plt.close(report_fig)
    
    return file_path


def _create_report_page(chart_fig: Figure, title: str, stats_text: str | None = None) -> Figure:
    """Create a professional report page with title, chart, and optional statistics."""
    import io
    from PIL import Image
    import numpy as np
    
    fig = plt.figure(figsize=(8.5, 11))
    
    # Add title section
    title_y = 0.97
    timestamp_y = 0.945
    separator_y = 0.93
    
    fig.text(0.5, title_y, title, ha='center', va='top', 
             fontsize=18, fontweight='bold', color='#1A1D24')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(0.5, timestamp_y, f"Generated: {timestamp}", ha='center', va='top',
             fontsize=9, color='#6B7080', style='italic')
    
    fig.add_artist(plt.Line2D([0.1, 0.9], [separator_y, separator_y], 
                               color='#D0D4DA', linewidth=1.5, 
                               transform=fig.transFigure))
    
    # Render chart to high-resolution image
    buf = io.BytesIO()
    chart_fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', 
                      facecolor='white', edgecolor='none')
    buf.seek(0)
    chart_img = Image.open(buf)
    
    # Calculate chart positioning
    img_width, img_height = chart_img.size
    img_aspect = img_width / img_height
    
    chart_start_y = separator_y - 0.01
    available_width = 0.8
    
    fig_width_inches = 8.5 * available_width
    chart_height_inches = fig_width_inches / img_aspect
    chart_height_fig = chart_height_inches / 11
    
    max_chart_height = chart_start_y - (0.28 if stats_text else 0.08)
    chart_height_fig = min(chart_height_fig, max_chart_height)
    chart_bottom_y = chart_start_y - chart_height_fig
    
    # Add chart
    chart_ax = fig.add_axes([0.1, chart_bottom_y, available_width, chart_height_fig])
    chart_ax.imshow(np.array(chart_img))
    chart_ax.axis('off')
    
    # Add statistics section
    if stats_text:
        stats_y_start = chart_bottom_y - 0.02
        
        fig.text(0.1, stats_y_start, "Statistics", ha='left', va='top',
                 fontsize=13, fontweight='bold', color='#1A1D24')
        
        fig.add_artist(plt.Line2D([0.1, 0.9], [stats_y_start - 0.02, stats_y_start - 0.02], 
                                   color='#D0D4DA', linewidth=1, 
                                   transform=fig.transFigure))
        
        fig.text(0.1, stats_y_start - 0.04, stats_text, ha='left', va='top',
                 fontsize=10, color='#2A2D35', family='monospace',
                 transform=fig.transFigure)
    
    buf.close()
    return fig


def export_comprehensive_report(
    trend_chart_generator,
    pie_chart_generator,
    bar_chart_generator,
    filename: str | None = None,
    stats_text: str | None = None,
    bar_text: str | None = None,
    title: str = "Comprehensive Report",
    save_directory: str | None = None
) -> str | None:
    """
    Export a comprehensive report with trend chart, pie chart, and bar chart to PDF.
    
    Args:
        trend_chart_generator: Callable that returns matplotlib Figure for trend chart
        pie_chart_generator: Callable that returns matplotlib Figure for pie chart
        bar_chart_generator: Callable that returns matplotlib Figure for bar chart
        filename: Optional filename (without extension). If None, uses timestamp
        stats_text: Optional statistics text to include in middle section
        bar_text: Optional text to display next to bar chart
        title: Title for the report
        save_directory: Directory to save the PDF. If None, prompts user for location
        
    Returns:
        str: Path to saved PDF file, or None if cancelled
        
    Example:
        export_comprehensive_report(
            trend_chart_generator=lambda: apartment_repo.create_occupancy_trend_graph(...),
            pie_chart_generator=lambda: apartment_repo.create_occupancy_pie_chart(...),
            bar_chart_generator=lambda: apartment_repo.create_revenue_bar_chart(...),
            filename="occupancy_report",
            title="Occupancy Analysis Report"
        )
    """
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}"
    
    # Remove .pdf extension if user included it
    if filename.endswith('.pdf'):
        filename = filename[:-4]
    
    # Prompt for save location if not provided
    if save_directory is None:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"{filename}.pdf",
            title="Save Report as PDF"
        )
        
        root.destroy()
        
        if not file_path:
            return None
    else:
        save_path = Path(save_directory)
        save_path.mkdir(parents=True, exist_ok=True)
        file_path = str(save_path / f"{filename}.pdf")
    
    # Generate all charts
    try:
        trend_fig = trend_chart_generator()
        pie_fig = pie_chart_generator()
        bar_fig = bar_chart_generator()
    except Exception as e:
        print(f"Error generating charts for comprehensive report: {e}")
        return None
    
    # Create PDF with single comprehensive page
    with PdfPages(file_path) as pdf:
        comprehensive_page = _create_comprehensive_page(
            trend_fig, pie_fig, bar_fig, title, stats_text, bar_text
        )
        pdf.savefig(comprehensive_page, dpi=300, bbox_inches='tight')
        plt.close(comprehensive_page)
        
        # Clean up generated figures
        plt.close(trend_fig)
        plt.close(pie_fig)
        plt.close(bar_fig)
    
    return file_path


def _create_comprehensive_page(
    trend_fig: Figure, 
    pie_fig: Figure, 
    bar_fig: Figure, 
    title: str, 
    stats_text: str | None = None,
    bar_text: str | None = None
) -> Figure:
    """Create a comprehensive single-page report with trend, pie, and bar charts."""
    import io
    from PIL import Image
    import numpy as np
    
    fig = plt.figure(figsize=(8.5, 11))
    
    # Title section
    title_y = 0.98
    timestamp_y = 0.96
    separator_y = 0.945
    
    fig.text(0.5, title_y, title, ha='center', va='top', 
             fontsize=16, fontweight='bold', color='#1A1D24')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(0.5, timestamp_y, f"Generated: {timestamp}", ha='center', va='top',
             fontsize=8, color='#6B7080', style='italic')
    
    fig.add_artist(plt.Line2D([0.1, 0.9], [separator_y, separator_y], 
                               color='#D0D4DA', linewidth=1.2, 
                               transform=fig.transFigure))
    
    # Render trend chart
    buf_trend = io.BytesIO()
    trend_fig.savefig(buf_trend, format='png', dpi=200, bbox_inches='tight', 
                      facecolor='white', edgecolor='none')
    buf_trend.seek(0)
    trend_img = Image.open(buf_trend)
    
    # Render pie chart
    buf_pie = io.BytesIO()
    pie_fig.savefig(buf_pie, format='png', dpi=200, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    buf_pie.seek(0)
    pie_img = Image.open(buf_pie)
    
    # Render bar chart
    buf_bar = io.BytesIO()
    bar_fig.savefig(buf_bar, format='png', dpi=200, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
    buf_bar.seek(0)
    bar_img = Image.open(buf_bar)
    
    # Layout positioning
    # Trend chart at top (full width, larger)
    trend_top = 0.93
    trend_height = 0.36
    trend_left = 0.08
    trend_width = 0.84
    
    trend_ax = fig.add_axes([trend_left, trend_top - trend_height, trend_width, trend_height])
    trend_ax.imshow(np.array(trend_img))
    trend_ax.axis('off')
    
    # Separator line under trend chart
    separator_y = trend_top - trend_height - 0.01
    fig.add_artist(plt.Line2D([0.1, 0.9], [separator_y, separator_y], 
                               color='#D0D4DA', linewidth=1.2, 
                               transform=fig.transFigure))
    
    # Stats and pie chart side by side (middle section)
    middle_top = separator_y - 0.02
    middle_height = 0.24
    
    # Stats on left (if provided) - with left margin
    stats_left = 0.12
    if stats_text:
        stats_top = middle_top - 0.02
        
        fig.text(stats_left, stats_top, "Statistics", ha='left', va='top',
                 fontsize=11, fontweight='bold', color='#1A1D24')
        
        fig.add_artist(plt.Line2D([stats_left, stats_left + 0.34], [stats_top - 0.015, stats_top - 0.015], 
                                   color='#D0D4DA', linewidth=1, 
                                   transform=fig.transFigure))
        
        fig.text(stats_left, stats_top - 0.03, stats_text, ha='left', va='top',
                 fontsize=9, color='#2A2D35', family='monospace',
                 transform=fig.transFigure)
    
    # Pie chart on right
    pie_left = 0.54
    pie_width = 0.38
    
    pie_ax = fig.add_axes([pie_left, middle_top - middle_height, pie_width, middle_height])
    pie_ax.imshow(np.array(pie_img))
    pie_ax.axis('off')
    
    # Separator line before bar chart
    bar_separator_y = middle_top - middle_height - 0.01
    fig.add_artist(plt.Line2D([0.1, 0.9], [bar_separator_y, bar_separator_y], 
                               color='#D0D4DA', linewidth=1.2, 
                               transform=fig.transFigure))
    
    # Bar chart on left side
    bar_top = bar_separator_y - 0.02
    bar_height = 0.24
    bar_left = 0.08
    bar_width = 0.46
    
    bar_ax = fig.add_axes([bar_left, bar_top - bar_height, bar_width, bar_height])
    bar_ax.imshow(np.array(bar_img))
    bar_ax.axis('off')
    
    # Bar chart analysis text on right
    if bar_text:
        bar_text_left = 0.58
        bar_text_top = bar_top - 0.02
        
        fig.text(bar_text_left, bar_text_top, "Revenue Analysis", ha='left', va='top',
                 fontsize=11, fontweight='bold', color='#1A1D24')
        
        fig.add_artist(plt.Line2D([bar_text_left, bar_text_left + 0.34], [bar_text_top - 0.015, bar_text_top - 0.015], 
                                   color='#D0D4DA', linewidth=1, 
                                   transform=fig.transFigure))
        
        fig.text(bar_text_left, bar_text_top - 0.03, bar_text, ha='left', va='top',
                 fontsize=9, color='#2A2D35', family='monospace',
                 transform=fig.transFigure)
    
    buf_trend.close()
    buf_pie.close()
    buf_bar.close()
    
    return fig
