"""Shared role-driven dashboard card loader."""

from __future__ import annotations

import customtkinter as ctk
import pages.components.page_elements as pe


def render_dashboard_cards(home_page, role, card_specs):
    """Render cards in declared order and row layout."""
    container = pe.ScrollableContainer(parent=home_page)
    rows: dict[int, object] = {}

    for card_spec in card_specs:
        row_index = int(card_spec["row"])
        builder = card_spec["builder"]
        kwargs = card_spec.get("kwargs", {})

        if row_index not in rows:
            rows[row_index] = pe.RowContainer(parent=container)

        builder(role, rows[row_index], **kwargs)

    return container


def render_dashboard_with_location_selector(home_page, role, card_specs, get_locations):
    """Render cards with a top-level location selector and reload behavior."""
    state = {"container": None}

    def build_cards():
        state["container"] = render_dashboard_cards(home_page, role, card_specs)

    def reload_content(selected_location):
        role.location = selected_location

        if state["container"] is not None:
            state["container"].pack_forget()
            state["container"].destroy()

        build_cards()

    if not role.location:
        location_frame = ctk.CTkFrame(home_page, fg_color="transparent")
        location_frame.pack(fill="x", padx=(25, 0), pady=0)

        try:
            all_locations = get_locations()
        except Exception as error:
            print(f"Error loading locations: {error}")
            all_locations = []

        if not all_locations:
            all_locations = [""]

        location_dropdown = ctk.CTkOptionMenu(
            location_frame,
            values=all_locations,
            command=reload_content,
        )
        location_dropdown.pack(side="left")
        pe.style_secondary_dropdown(location_dropdown)
        role.location = location_dropdown.get()

    build_cards()
    return state["container"]
