"""Contributors: Aaron Antal-Bento (23013693), Ahmed AlShamy (24045361)

UI controls helpers for reusable widgets and layout elements."""

import customtkinter as ctk

from pages.components.config.theme import THEME
from pages.components.scrollable_option_menu import ScrollableDropdown
from pages.components.style_utils import style_secondary_dropdown
from database_operations.database_repositories import get_all_cities

def normalize_location_value(location_value: str | None, all_value: str = "all") -> str:
    """Normalize UI location values to repository-friendly values."""
    if location_value == "All Locations":
        return all_value
    return location_value or all_value


def create_refresh_button(parent, command, side="left", padx=(12, 0), square=False):
    """Create a standardized refresh button."""
    button = ctk.CTkButton(
        parent,
        text="\u27f3 Refresh" if not square else "\u27f3",
        command=command,
        height=30 if square else 32,
        width=30 if square else 120,
        fg_color=THEME.colors.secondary_gray,
        hover_color=THEME.colors.secondary_gray_hover,
        text_color=THEME.colors.text,
    )
    button.pack(side=side, padx=padx)
    return button


def create_debounced_refresh(widget, callback, delay_ms=150):
    """Create a debounced refresh function for dropdowns."""
    refresh_timer = {"id": None}

    def schedule_refresh(_choice=None):
        if refresh_timer["id"] is not None:
            try:
                widget.after_cancel(refresh_timer["id"])
            except Exception:
                pass
        refresh_timer["id"] = widget.after(delay_ms, callback)

    return refresh_timer, schedule_refresh


def create_popup_header_with_location(content):
    """Create a popup header with location dropdown."""
    header = ctk.CTkFrame(content, fg_color="transparent")
    header.pack(fill="x", padx=10, pady=(5, 10))

    ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(
        side="left", padx=(0, 8)
    )

    try:
        cities = ["All Locations"] + get_all_cities()
    except Exception as e:
        print(f"Error loading cities: {e}")
        cities = ["All Locations"]

    location_dropdown = ctk.CTkComboBox(header, values=cities, width=220, font=("Arial", 13))
    location_dropdown.set("All Locations")
    location_dropdown.pack(side="left")

    return header, location_dropdown


def content_separator(parent, pady=(5, 10), padx=15):
    """Add a visual separator line."""
    separator = ctk.CTkFrame(parent, height=2, fg_color="gray35")
    separator.pack(fill="x", pady=pady, padx=padx)
    return separator


def vertical_divider(parent, pady=5, padx=(0, 5)):
    """Add a vertical separator line."""
    separator = ctk.CTkFrame(parent, width=2, height=1, fg_color="gray35")
    separator.pack(fill="y", side="left", padx=padx, pady=pady)
    return separator


def create_dynamic_dropdown_with_refresh(
    parent,
    data_fetcher,
    display_formatter=lambda x: (str(x), x),
    empty_message="No items available",
):
    """Create a dropdown with dynamic data and refresh button."""
    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(fill="x", padx=0, pady=0)

    dropdown = ScrollableDropdown(
        container,
        values=["Loading..."],
        dropdown_max_visible_rows=10,
        font=("Arial", 12),
    )
    dropdown.pack(side="left", expand=True, fill="x", pady=0)
    dropdown.set("Loading...")
    style_secondary_dropdown(dropdown)

    data_map = {}

    def refresh():
        try:
            data = data_fetcher()

            if not data:
                dropdown.configure(values=[empty_message])
                dropdown.set(empty_message)
                data_map.clear()
                return

            options = []
            data_map.clear()
            for item in data:
                display, value = display_formatter(item)
                options.append(display)
                data_map[display] = value

            dropdown.configure(values=options)
            dropdown.set(options[0])
        except Exception as e:
            dropdown.configure(values=[f"Error: {str(e)}"])
            dropdown.set(f"Error: {str(e)}")
            data_map.clear()

    create_refresh_button(container, refresh, side="left", padx=(5, 0), square=True)
    refresh()

    return dropdown, data_map, refresh
