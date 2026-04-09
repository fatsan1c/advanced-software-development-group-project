"""Contributors: Ahmed AlShamy (24045361)

Date helper functions, including calendar popup integration."""

from datetime import datetime

import customtkinter as ctk

from pages.components.config.theme import THEME
from pages.components.popup_utils import enable_click_outside_to_close

try:
    from tkcalendar import Calendar
except Exception:
    Calendar = None


def parse_date_string(date_str):
    """Parse YYYY-MM-DD date string to a date object."""
    s = (date_str or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def open_date_picker(entry_widget, parent_window):
    """Open a calendar date picker popup for an entry widget."""
    popup = ctk.CTkToplevel(parent_window)
    popup.title("Select Date")
    popup.geometry("360x430")
    popup.resizable(False, False)
    popup.transient(parent_window)
    enable_click_outside_to_close(popup, parent_window)

    selected = parse_date_string(entry_widget.get()) or datetime.now().date()
    mode = str(ctk.get_appearance_mode()).lower()
    is_dark = mode == "dark"

    shell = ctk.CTkFrame(
        popup,
        corner_radius=12,
        fg_color=("#F3F4F6", "#1F232A"),
        border_width=1,
        border_color=("#D8DCE2", "#2C313A"),
    )
    shell.pack(fill="both", expand=True, padx=8, pady=8)

    ctk.CTkLabel(
        shell,
        text="Pick a Date",
        font=("Arial", 24, "bold"),
        text_color=("#22252B", "#E9ECF2"),
    ).pack(anchor="w", padx=12, pady=(12, 4))
    ctk.CTkLabel(
        shell,
        text="Format: YYYY-MM-DD",
        font=("Arial", 12),
        text_color=("#5E6672", "#AAB2BE"),
    ).pack(anchor="w", padx=12, pady=(0, 8))

    if Calendar is None:
        ctk.CTkLabel(
            shell,
            text="Calendar unavailable.\nInstall tkcalendar package.",
            justify="center",
            font=("Arial", 12),
        ).pack(pady=18)
        ctk.CTkButton(shell, text="Close", command=popup.destroy, width=120).pack(pady=(10, 0))
        return

    cal_kwargs = {
        "selectmode": "day",
        "date_pattern": "yyyy-mm-dd",
        "year": selected.year,
        "month": selected.month,
        "day": selected.day,
    }

    if is_dark:
        cal_kwargs.update(
            {
                "font": ("Arial", 17),
                "headersfont": ("Arial", 15, "bold"),
                "background": "#2A2F36",
                "foreground": "#E9ECF2",
                "bordercolor": "#2A2F36",
                "headersbackground": "#222831",
                "headersforeground": "#E9ECF2",
                "normalbackground": "#2A2F36",
                "normalforeground": "#E9ECF2",
                "weekendbackground": "#2A2F36",
                "weekendforeground": "#E9ECF2",
                "othermonthbackground": "#2A2F36",
                "othermonthforeground": "#7F8A98",
                "selectbackground": THEME.colors.primary_blue,
                "selectforeground": "#FFFFFF",
            }
        )
    else:
        cal_kwargs.update(
            {
                "font": ("Arial", 17),
                "headersfont": ("Arial", 15, "bold"),
                "background": "#FFFFFF",
                "foreground": "#1B2430",
                "bordercolor": "#D7DBE2",
                "headersbackground": "#EEF2F7",
                "headersforeground": "#1B2430",
                "normalbackground": "#FFFFFF",
                "normalforeground": "#1B2430",
                "selectbackground": THEME.colors.primary_blue,
                "selectforeground": "#FFFFFF",
            }
        )

    cal = Calendar(shell, **cal_kwargs, showweeknumbers=False)
    cal.pack(fill="both", expand=True, padx=12, pady=(4, 10))

    def apply_date():
        entry_widget.delete(0, "end")
        entry_widget.insert(0, cal.get_date())
        popup.destroy()

    btn_row = ctk.CTkFrame(shell, fg_color="transparent")
    btn_row.pack(fill="x", padx=10, pady=(0, 10))

    ctk.CTkButton(
        btn_row,
        text="Cancel",
        command=popup.destroy,
        width=104,
        height=34,
        font=("Arial", 14),
        fg_color=THEME.colors.secondary_gray,
        hover_color=THEME.colors.secondary_gray_hover,
        text_color=THEME.colors.text,
    ).pack(side="left")
    ctk.CTkButton(
        btn_row,
        text="Use Date",
        command=apply_date,
        width=104,
        height=34,
        font=("Arial", 14),
        fg_color=THEME.colors.primary_blue,
        hover_color=THEME.colors.primary_blue_hover,
    ).pack(side="right")
