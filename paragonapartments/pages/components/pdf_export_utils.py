"""Contributors: Aaron Antal-Bento (23013693)

Class-based PDF export service and UI helpers."""

from __future__ import annotations

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import customtkinter as ctk
import matplotlib
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from PIL import Image
from tkinter import filedialog

from pages.components.config.theme import THEME
from pages.components.popup_utils import center_popup, enable_click_outside_to_close

matplotlib.use("Agg")
import matplotlib.pyplot as plt


class PDFReportExporter:
    """Owns chart/report rendering and PDF file generation."""

    def export_chart_to_pdf(
        self,
        fig: Figure,
        filename: str | None = None,
        stats_text: str | None = None,
        title: str = "Report",
        save_directory: str | None = None,
    ) -> str | None:
        """Export a single chart report page to PDF."""
        safe_filename = self._normalize_filename(filename)
        file_path = self._resolve_save_path(safe_filename, save_directory)
        if not file_path:
            return None

        with PdfPages(file_path) as pdf:
            report_fig = self._create_report_page(fig, title, stats_text)
            pdf.savefig(report_fig, dpi=300, bbox_inches="tight")
            plt.close(report_fig)

        return file_path

    def export_comprehensive_report(
        self,
        trend_chart_generator: Callable[[], Figure],
        pie_chart_generator: Callable[[], Figure],
        bar_chart_generator: Callable[[], Figure],
        filename: str | None = None,
        stats_text: str | None = None,
        bar_text: str | None = None,
        title: str = "Comprehensive Report",
        save_directory: str | None = None,
    ) -> str | None:
        """Export a single-page trend/pie/bar comprehensive report to PDF."""
        safe_filename = self._normalize_filename(filename)
        file_path = self._resolve_save_path(safe_filename, save_directory)
        if not file_path:
            return None

        try:
            trend_fig = trend_chart_generator()
            pie_fig = pie_chart_generator()
            bar_fig = bar_chart_generator()
        except Exception as exc:
            print(f"Error generating charts for comprehensive report: {exc}")
            return None

        with PdfPages(file_path) as pdf:
            comprehensive_page = self._create_comprehensive_page(
                trend_fig, pie_fig, bar_fig, title, stats_text, bar_text
            )
            pdf.savefig(comprehensive_page, dpi=300, bbox_inches="tight")
            plt.close(comprehensive_page)

        plt.close(trend_fig)
        plt.close(pie_fig)
        plt.close(bar_fig)
        return file_path

    def _normalize_filename(self, filename: str | None) -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"report_{timestamp}"
        return filename[:-4] if filename.endswith(".pdf") else filename

    def _resolve_save_path(self, filename: str, save_directory: str | None) -> str | None:
        if save_directory is None:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            try:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=f"{filename}.pdf",
                    title="Save Report as PDF",
                )
            finally:
                root.destroy()
            return file_path or None

        save_path = Path(save_directory)
        save_path.mkdir(parents=True, exist_ok=True)
        return str(save_path / f"{filename}.pdf")

    def _render_figure_to_image(self, fig: Figure, dpi: int) -> Image.Image:
        buffer = io.BytesIO()
        fig.savefig(
            buffer,
            format="png",
            dpi=dpi,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )
        buffer.seek(0)
        image = Image.open(buffer).copy()
        buffer.close()
        return image

    def _create_report_page(self, chart_fig: Figure, title: str, stats_text: str | None) -> Figure:
        fig = plt.figure(figsize=(8.5, 11))

        title_y = 0.97
        timestamp_y = 0.945
        separator_y = 0.93

        fig.text(0.5, title_y, title, ha="center", va="top", fontsize=18, fontweight="bold", color="#1A1D24")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(
            0.5,
            timestamp_y,
            f"Generated: {timestamp}",
            ha="center",
            va="top",
            fontsize=9,
            color="#6B7080",
            style="italic",
        )
        fig.add_artist(
            plt.Line2D([0.1, 0.9], [separator_y, separator_y], color="#D0D4DA", linewidth=1.5, transform=fig.transFigure)
        )

        chart_img = self._render_figure_to_image(chart_fig, dpi=300)
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

        chart_ax = fig.add_axes([0.1, chart_bottom_y, available_width, chart_height_fig])
        chart_ax.imshow(np.array(chart_img))
        chart_ax.axis("off")

        if stats_text:
            stats_y_start = chart_bottom_y - 0.02
            fig.text(
                0.1,
                stats_y_start,
                "Statistics",
                ha="left",
                va="top",
                fontsize=13,
                fontweight="bold",
                color="#1A1D24",
            )
            fig.add_artist(
                plt.Line2D(
                    [0.1, 0.9],
                    [stats_y_start - 0.02, stats_y_start - 0.02],
                    color="#D0D4DA",
                    linewidth=1,
                    transform=fig.transFigure,
                )
            )
            fig.text(
                0.1,
                stats_y_start - 0.04,
                stats_text,
                ha="left",
                va="top",
                fontsize=10,
                color="#2A2D35",
                family="monospace",
                transform=fig.transFigure,
            )

        return fig

    def _create_comprehensive_page(
        self,
        trend_fig: Figure,
        pie_fig: Figure,
        bar_fig: Figure,
        title: str,
        stats_text: str | None,
        bar_text: str | None,
    ) -> Figure:
        fig = plt.figure(figsize=(8.5, 11))

        title_y = 0.98
        timestamp_y = 0.96
        separator_y = 0.945

        fig.text(0.5, title_y, title, ha="center", va="top", fontsize=16, fontweight="bold", color="#1A1D24")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(
            0.5,
            timestamp_y,
            f"Generated: {timestamp}",
            ha="center",
            va="top",
            fontsize=8,
            color="#6B7080",
            style="italic",
        )
        fig.add_artist(
            plt.Line2D([0.1, 0.9], [separator_y, separator_y], color="#D0D4DA", linewidth=1.2, transform=fig.transFigure)
        )

        trend_img = self._render_figure_to_image(trend_fig, dpi=200)
        pie_img = self._render_figure_to_image(pie_fig, dpi=200)
        bar_img = self._render_figure_to_image(bar_fig, dpi=200)

        trend_top = 0.93
        trend_height = 0.36
        trend_left = 0.08
        trend_width = 0.84
        trend_ax = fig.add_axes([trend_left, trend_top - trend_height, trend_width, trend_height])
        trend_ax.imshow(np.array(trend_img))
        trend_ax.axis("off")

        separator_y = trend_top - trend_height - 0.01
        fig.add_artist(
            plt.Line2D([0.1, 0.9], [separator_y, separator_y], color="#D0D4DA", linewidth=1.2, transform=fig.transFigure)
        )

        middle_top = separator_y - 0.02
        middle_height = 0.24

        stats_left = 0.12
        if stats_text:
            stats_top = middle_top - 0.02
            fig.text(
                stats_left,
                stats_top,
                "Statistics",
                ha="left",
                va="top",
                fontsize=11,
                fontweight="bold",
                color="#1A1D24",
            )
            fig.add_artist(
                plt.Line2D(
                    [stats_left, stats_left + 0.34],
                    [stats_top - 0.015, stats_top - 0.015],
                    color="#D0D4DA",
                    linewidth=1,
                    transform=fig.transFigure,
                )
            )
            fig.text(
                stats_left,
                stats_top - 0.03,
                stats_text,
                ha="left",
                va="top",
                fontsize=9,
                color="#2A2D35",
                family="monospace",
                transform=fig.transFigure,
            )

        pie_ax = fig.add_axes([0.54, middle_top - middle_height, 0.38, middle_height])
        pie_ax.imshow(np.array(pie_img))
        pie_ax.axis("off")

        bar_separator_y = middle_top - middle_height - 0.01
        fig.add_artist(
            plt.Line2D([0.1, 0.9], [bar_separator_y, bar_separator_y], color="#D0D4DA", linewidth=1.2, transform=fig.transFigure)
        )

        bar_top = bar_separator_y - 0.02
        bar_height = 0.24
        bar_ax = fig.add_axes([0.08, bar_top - bar_height, 0.46, bar_height])
        bar_ax.imshow(np.array(bar_img))
        bar_ax.axis("off")

        if bar_text:
            bar_text_left = 0.58
            bar_text_top = bar_top - 0.02
            fig.text(
                bar_text_left,
                bar_text_top,
                "Revenue Analysis",
                ha="left",
                va="top",
                fontsize=11,
                fontweight="bold",
                color="#1A1D24",
            )
            fig.add_artist(
                plt.Line2D(
                    [bar_text_left, bar_text_left + 0.34],
                    [bar_text_top - 0.015, bar_text_top - 0.015],
                    color="#D0D4DA",
                    linewidth=1,
                    transform=fig.transFigure,
                )
            )
            fig.text(
                bar_text_left,
                bar_text_top - 0.03,
                bar_text,
                ha="left",
                va="top",
                fontsize=9,
                color="#2A2D35",
                family="monospace",
                transform=fig.transFigure,
            )

        return fig


class PDFExportUI:
    """Builds export buttons and export feedback popups."""

    def __init__(self, exporter: PDFReportExporter | None = None) -> None:
        self.exporter = exporter or PDFReportExporter()

    def _load_export_icon(self, variant: str) -> ctk.CTkImage | None:
        if variant not in ("inline", "popup"):
            return None

        try:
            icons_dir = Path(__file__).resolve().parents[2] / "icons"
            upload_icon_path_light = icons_dir / "upload_icon.png"
            upload_icon_path_dark = icons_dir / "upload_icon_dark.png"
            icon_size = (18, 18) if variant == "inline" else (16, 16)
            return ctk.CTkImage(
                light_image=Image.open(upload_icon_path_light),
                dark_image=Image.open(upload_icon_path_dark),
                size=icon_size,
            )
        except Exception as exc:
            print(f"Warning: Could not load upload icon: {exc}")
            return None

    def _create_export_button_widget(
        self,
        parent: Any,
        command: Callable[[], None],
        upload_icon: ctk.CTkImage | None,
        variant: str,
        button_text: str,
        button_width: int,
        pady: int,
        padx: int,
    ):
        if variant == "inline":
            button_config = {
                "master": parent,
                "text": "" if upload_icon else "^",
                "command": command,
                "width": 40,
                "height": 40,
                "font": ("Arial", 14, "bold"),
                "corner_radius": THEME.radii.button,
                "fg_color": THEME.colors.secondary_gray,
                "hover_color": THEME.colors.secondary_gray_hover,
                "text_color": THEME.colors.text,
            }
            if upload_icon:
                button_config["image"] = upload_icon
            button = ctk.CTkButton(**button_config)
            button.pack(side="left", pady=0, padx=0)
            return button

        if variant == "popup":
            button_config = {
                "master": parent,
                "text": "Export",
                "command": command,
                "width": 100,
                "height": 32,
                "font": ("Arial", 14, "bold"),
                "corner_radius": THEME.radii.button,
                "fg_color": THEME.colors.secondary_gray,
                "hover_color": THEME.colors.secondary_gray_hover,
                "text_color": THEME.colors.text,
            }
            if upload_icon:
                button_config["image"] = upload_icon
                button_config["compound"] = "left"
            button = ctk.CTkButton(**button_config)
            button.pack(side="right", pady=0, padx=0)
            return button

        button = ctk.CTkButton(
            parent,
            text=button_text,
            command=command,
            width=button_width,
            height=36,
            font=("Arial", 13),
            corner_radius=THEME.radii.button,
            fg_color=THEME.colors.secondary_gray,
            hover_color=THEME.colors.secondary_gray_hover,
            text_color=THEME.colors.text,
        )
        button.pack(pady=pady, padx=padx)
        return button

    def show_pdf_export_success_popup(self, parent_widget: Any, pdf_path: str) -> None:
        success_popup = ctk.CTkToplevel(parent_widget)
        success_popup.title("Export Successful")
        success_popup.geometry("400x170")
        success_popup.resizable(False, False)
        success_popup.transient(parent_widget)

        center_popup(success_popup, 400, 170)
        enable_click_outside_to_close(success_popup, parent_widget)

        ctk.CTkLabel(
            success_popup,
            text="PDF Exported Successfully",
            font=("Arial", 16, "bold"),
            text_color="#2BA89A",
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            success_popup,
            text=f"Saved to:\n{pdf_path}",
            font=("Arial", 11),
            wraplength=400,
        ).pack(pady=(0, 15))

        button_frame = ctk.CTkFrame(success_popup, fg_color="transparent")
        button_frame.pack(pady=(0, 15))

        def open_pdf():
            try:
                os.startfile(pdf_path)
                success_popup.destroy()
            except Exception:
                import subprocess

                try:
                    subprocess.run(["xdg-open", pdf_path], check=False)
                except Exception:
                    pass

        ctk.CTkButton(
            button_frame,
            text="Open",
            command=open_pdf,
            width=100,
            height=32,
            fg_color=THEME.colors.primary_blue,
            hover_color=THEME.colors.primary_blue_hover,
            corner_radius=THEME.radii.button,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="Close",
            command=success_popup.destroy,
            width=100,
            height=32,
            fg_color=THEME.colors.secondary_gray,
            hover_color=THEME.colors.secondary_gray_hover,
            corner_radius=THEME.radii.button,
        ).pack(side="left")

    def show_pdf_export_error_popup(self, parent_widget: Any, error_message: str) -> None:
        error_popup = ctk.CTkToplevel(parent_widget)
        error_popup.title("Export Failed")
        error_popup.geometry("400x150")
        error_popup.resizable(False, False)
        error_popup.transient(parent_widget)

        center_popup(error_popup, 400, 150)
        enable_click_outside_to_close(error_popup, parent_widget)

        ctk.CTkLabel(
            error_popup,
            text="Export Failed",
            font=("Arial", 16, "bold"),
            text_color="#C75B6D",
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            error_popup,
            text=f"Error: {error_message}",
            font=("Arial", 11),
            wraplength=350,
        ).pack(pady=(0, 15))

        ctk.CTkButton(error_popup, text="OK", command=error_popup.destroy, width=100, height=32).pack(
            pady=(0, 15)
        )

    def create_export_button(
        self,
        parent: Any,
        chart_generator: Callable[[], Any] | Any = None,
        pie_chart_generator: Callable[[], Figure] | None = None,
        bar_chart_generator: Callable[[], Figure] | None = None,
        stats_generator: Callable[[], str | None] | None = None,
        bar_text_generator: Callable[[], str | None] | None = None,
        export_title: str = "Report",
        export_filename: str = "report",
        button_text: str = "Export to PDF",
        button_width: int = 180,
        pady: int = 5,
        padx: int = 5,
        variant: str = "standard",
    ):
        """Create a unified export button for chart or comprehensive report exports."""

        def handle_export() -> None:
            try:
                is_comprehensive = bool(pie_chart_generator and bar_chart_generator)
                stats = stats_generator() if stats_generator and callable(stats_generator) else None

                if is_comprehensive:
                    bar_text = bar_text_generator() if bar_text_generator and callable(bar_text_generator) else None
                    pdf_path = self.exporter.export_comprehensive_report(
                        trend_chart_generator=chart_generator,
                        pie_chart_generator=pie_chart_generator,
                        bar_chart_generator=bar_chart_generator,
                        filename=export_filename,
                        stats_text=stats,
                        bar_text=bar_text,
                        title=export_title,
                    )
                else:
                    obj = chart_generator() if callable(chart_generator) else chart_generator
                    fig = obj.figure if hasattr(obj, "figure") else obj
                    if fig is None:
                        raise ValueError("No chart available to export")
                    pdf_path = self.exporter.export_chart_to_pdf(
                        fig,
                        filename=export_filename,
                        stats_text=stats,
                        title=export_title,
                    )

                if pdf_path:
                    self.show_pdf_export_success_popup(parent.winfo_toplevel(), pdf_path)
            except Exception as exc:
                self.show_pdf_export_error_popup(parent.winfo_toplevel(), str(exc))

        command = handle_export if chart_generator is not None else lambda: None
        upload_icon = self._load_export_icon(variant)
        return self._create_export_button_widget(
            parent,
            command,
            upload_icon,
            variant,
            button_text,
            button_width,
            pady,
            padx,
        )

    def create_comprehensive_export_button(
        self,
        parent: Any,
        trend_chart_generator: Callable[[], Figure],
        pie_chart_generator: Callable[[], Figure],
        bar_chart_generator: Callable[[], Figure],
        stats_generator: Callable[[], str | None] | None = None,
        bar_text_generator: Callable[[], str | None] | None = None,
        export_title: str = "Comprehensive Report",
        export_filename: str = "comprehensive_report",
        button_text: str = "Export Comprehensive Report",
        variant: str = "standard",
    ):
        return self.create_export_button(
            parent=parent,
            chart_generator=trend_chart_generator,
            pie_chart_generator=pie_chart_generator,
            bar_chart_generator=bar_chart_generator,
            stats_generator=stats_generator,
            bar_text_generator=bar_text_generator,
            export_title=export_title,
            export_filename=export_filename,
            button_text=button_text,
            variant=variant,
        )

    def create_export_pdf_button(
        self,
        parent: Any,
        canvas_or_fig: Any = None,
        default_filename: str | None = None,
        stats_text: Callable[[], str | None] | str | None = None,
        title: str = "Report",
        button_text: str = "Export to PDF",
        button_width: int = 180,
        pady: int = 5,
        padx: int = 5,
        variant: str = "standard",
    ):
        stats_generator = stats_text if callable(stats_text) else (lambda: stats_text if stats_text else None)
        return self.create_export_button(
            parent=parent,
            chart_generator=canvas_or_fig,
            stats_generator=stats_generator,
            export_title=title,
            export_filename=default_filename or "report",
            button_text=button_text,
            button_width=button_width,
            pady=pady,
            padx=padx,
            variant=variant,
        )
