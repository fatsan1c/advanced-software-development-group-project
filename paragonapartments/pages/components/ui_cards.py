"""
Contributors: Aaron Antal-Bento (23013693), Ahmed AlShamy (24045361)

UI card components for displaying organized content.

This module provides card-style UI elements including:
- FunctionCard: Main card content container for role-based functions
- ActionButton: Standard action button with consistent sizing
- PopupCard: Modal popup with overlay and trigger support
- InfoBadge: Styled info badge with yellow/brown theme
- LocationDropdownWithLabel: Location selection dropdown
- StatCard: Metric display card value label
- StatsGrid: Container for stat cards
"""

import customtkinter as ctk
from pages.components.config.theme import THEME
from database_operations.database_repositories import get_all_cities
from pages.components.style_utils import style_secondary_dropdown
from pages.components.ui_controls_utils import content_separator


class FunctionCard(ctk.CTkFrame):
    """Card content frame with a standard titled container wrapper."""

    def __init__(self, parent, title, side="left", anchor="nw", pady=10, padx=10):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(side=side, pady=pady, padx=padx, anchor=anchor, expand=True, fill="both")

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 18, "bold"),
            anchor="w",
        ).pack(padx=15, pady=(10, 5))

        content_separator(card, pady=(0, 5))

        super().__init__(card, fg_color="transparent")
        self.card = card
        self.pack(fill="both", expand=True, padx=15, pady=(5, 15))


class ActionButton(ctk.CTkButton):
    """Standard action button with consistent sizing presets."""

    SIZES = {
        "small": (180, 36, 14),
        "medium": (250, 40, 16),
        "large": (350, 45, 18),
        "full": (0, 45, 16),
    }

    def __init__(self, parent, text, command, size="medium", pady=5, padx=5, side=None):
        width, height, font_size = self.SIZES.get(size, self.SIZES["medium"])
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            font=("Arial", font_size),
            corner_radius=8,
        )

        if size == "full":
            self.pack(pady=pady, padx=padx, side=side, fill="x")
        else:
            self.pack(pady=pady, padx=padx, side=side)


class PopupCard:
    """Popup overlay helper with optional trigger button and open callback."""

    def __init__(self, parent, title, small=False, button_text="Open", button_size="medium", generate_button=True):
        self.parent = parent
        self.title = title
        self.small = small
        self.overlay = None
        self.popup = None
        self.button = ActionButton(parent, button_text, self.open_popup, size=button_size) if generate_button else None

    def __iter__(self):
        yield self.button
        yield self.open_popup

    def close_popup(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            self.popup = None

    def open_popup(self):
        self.close_popup()

        top_level = self.parent.winfo_toplevel()
        overlay = ctk.CTkFrame(top_level, fg_color="transparent")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.lift()
        overlay.bind("<Button-1>", lambda e: self.close_popup())

        popup = ctk.CTkFrame(overlay, corner_radius=10)
        if not self.small:
            popup.place(relx=0.015, rely=0.015, relwidth=0.97, relheight=0.97)
        else:
            popup.place(relx=0.5, rely=0.5, anchor="center")

        self.overlay = overlay
        self.popup = popup
        popup.bind("<Button-1>", lambda e: "break")

        header = ctk.CTkFrame(popup, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            header,
            text=self.title,
            font=("Arial", 18, "bold"),
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=30,
            height=30,
            font=("Arial", 18),
            command=self.close_popup,
            fg_color=THEME.colors.secondary_gray,
            hover_color=THEME.colors.secondary_gray_hover,
            text_color=THEME.colors.text,
        )
        close_btn.pack(side="right")

        content_separator(popup, pady=(0, 5))

        content = ctk.CTkFrame(popup, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        return content


class InfoBadge(ctk.CTkLabel):
    """Styled yellow/brown information badge."""

    def __init__(self, parent, text: str, side="left", padx=6):
        super().__init__(
            parent,
            text=text,
            font=("Arial", 12, "bold"),
            text_color=("#6E4B00", "#F5D27A"),
            fg_color=("#F4D28A", "#4B360D"),
            corner_radius=THEME.radii.input,
            padx=10,
            pady=6,
        )
        self.pack(side=side, padx=padx)


class LocationDropdownWithLabel(ctk.CTkComboBox):
    """Location selector combo box with an attached label wrapper."""

    def __init__(self, parent, initial_value="All Locations", side="left", padx=(12, 0)):
        location_wrap = ctk.CTkFrame(parent, fg_color="transparent")
        location_wrap.pack(side=side, padx=padx)
        self.wrapper = location_wrap

        ctk.CTkLabel(
            location_wrap,
            text="Location",
            font=("Arial", 13, "bold"),
            text_color=THEME.colors.text,
        ).pack(side="left", padx=(0, 10))

        try:
            cities = ["All Locations"] + get_all_cities()
        except Exception as e:
            print(f"Error loading cities: {e}")
            cities = ["All Locations"]

        super().__init__(location_wrap, values=cities, width=240, font=("Arial", 13))
        self.set(initial_value)
        self.pack(side="left")
        style_secondary_dropdown(self)


class StatCard(ctk.CTkLabel):
    """Metric value label inside a standardized stat card."""

    def __init__(self, parent, title: str, default_value: str = "0"):
        card = ctk.CTkFrame(
            parent,
            corner_radius=THEME.radii.box,
            fg_color=("gray92", "gray17"),
            border_width=1,
            border_color=THEME.colors.secondary_gray,
        )
        card.pack(side="left", expand=True, fill="both", padx=6, ipadx=8, ipady=10)
        self.card = card

        ctk.CTkLabel(
            card,
            text=title.upper(),
            font=("Arial", 11, "bold"),
            text_color=("gray45", "gray70"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 0))

        super().__init__(
            card,
            text=default_value,
            font=("Arial", 20, "bold"),
            text_color=("#3B8ED0", "#3B8ED0"),
            anchor="w",
        )
        self.pack(fill="x", padx=12, pady=(2, 8))


class StatsGrid(ctk.CTkFrame):
    """Horizontal container for stat cards."""

    def __init__(self, parent, pady=(0, 4)):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="x", pady=pady)
