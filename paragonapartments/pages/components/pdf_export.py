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


def export_multiple_charts_to_pdf(
    figures: list[Figure],
    filename: str | None = None,
    title: str = "Report",
    save_directory: str | None = None
) -> str | None:
    """
    Export multiple matplotlib figures to a single PDF.
    
    Args:
        figures: List of Matplotlib Figure objects to export
        filename: Optional filename (without extension). If None, uses timestamp
        title: Title for the report
        save_directory: Directory to save the PDF. If None, prompts user for location
        
    Returns:
        str: Path to saved PDF file, or None if cancelled
        
    Example:
        fig1 = create_bar_chart(...)
        fig2 = create_trend_chart(...)
        pdf_path = export_multiple_charts_to_pdf([fig1, fig2], "quarterly_report")
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
    
    # Create PDF with multiple pages
    with PdfPages(file_path) as pdf:
        for fig in figures:
            pdf.savefig(fig, dpi=300, bbox_inches='tight')
    
    return file_path


def get_figure_from_canvas(canvas) -> Figure | None:
    """
    Extract matplotlib Figure from FigureCanvasTkAgg.
    
    Args:
        canvas: FigureCanvasTkAgg object returned by chart_utils functions
        
    Returns:
        Figure: The underlying matplotlib Figure, or None if extraction fails
        
    Example:
        canvas = create_bar_chart(parent, ...)
        fig = get_figure_from_canvas(canvas)
        export_chart_to_pdf(fig, "my_chart")
    """
    try:
        if hasattr(canvas, 'figure'):
            return canvas.figure
        return None
    except Exception:
        return None
