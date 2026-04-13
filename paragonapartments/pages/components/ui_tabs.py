"""Contributors: Aaron Antal-Bento (23013693)

Tab-style menu components for dashboard navigation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from pages.components.config.theme import THEME
from pages.components.style_utils import style_secondary_dropdown


class DashboardTabsMenu(ctk.CTkFrame):
    """Top menu with tab-style buttons and optional location context."""

    def __init__(
        self,
        parent,
        tabs: list[tuple[str, str]],
        on_tab_selected: Callable[[str, str], Any] | None = None,
        on_location_changed: Callable[[str, str], Any] | None = None,
        title: str = "Dashboard Selector",
        get_locations: Callable[[], list[str]] | None = None,
        initial_location: str = "All Locations",
        default_tab_key: str | None = None,
        padx: int = 20,
        pady: tuple[int, int] = (0, 8),
    ):
        super().__init__(
            parent,
            corner_radius=THEME.radii.box,
            border_width=1,
            border_color=THEME.colors.secondary_gray,
            fg_color=THEME.colors.surface_card,
        )
        self.pack(fill="x", padx=padx, pady=pady)

        self._on_tab_selected = on_tab_selected
        self._on_location_changed = on_location_changed
        self._tab_buttons: dict[str, ctk.CTkButton] = {}
        self._active_tab_key: str | None = None
        self._location_dropdown: ctk.CTkComboBox | None = None

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 4))

        heading = ctk.CTkFrame(header, fg_color="transparent")
        heading.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            heading,
            text=title,
            font=THEME.typography.title,
            text_color=THEME.colors.text,
            anchor="w",
        ).pack(anchor="w")

        if get_locations is not None:
            self._create_location_selector(header, get_locations, initial_location)

        tabs_row = ctk.CTkFrame(self, fg_color="transparent")
        tabs_row.pack(fill="x", padx=12, pady=(4, 12))

        for idx in range(len(tabs)):
            tabs_row.grid_columnconfigure(idx, weight=1, uniform="dashboard_tabs")

        for index, (label, key) in enumerate(tabs):
            button = ctk.CTkButton(
                tabs_row,
                text=label,
                height=36,
                corner_radius=THEME.radii.button,
                font=THEME.typography.body_md,
                command=lambda tab_key=key: self.select_tab(tab_key, invoke_callback=True),
            )
            button.grid(row=0, column=index, sticky="ew", padx=4, pady=0)
            self._tab_buttons[key] = button
            self._set_tab_style(key, is_active=False)

        if default_tab_key and default_tab_key in self._tab_buttons:
            self.select_tab(default_tab_key, invoke_callback=False)

    def _create_location_selector(
        self,
        parent,
        get_locations: Callable[[], list[str]],
        initial_location: str,
    ):
        location_wrap = ctk.CTkFrame(parent, fg_color="transparent")
        location_wrap.pack(side="right")

        ctk.CTkLabel(
            location_wrap,
            text="Location",
            font=THEME.typography.body_md,
            text_color=THEME.colors.text,
        ).pack(side="left", padx=(0, 10))

        locations = ["All Locations"]
        try:
            locations.extend(location for location in get_locations() if location)
        except Exception as error:
            print(f"Error loading dashboard locations: {error}")

        deduped_locations = []
        seen: set[str] = set()
        for location in locations:
            if location not in seen:
                seen.add(location)
                deduped_locations.append(location)

        self._location_dropdown = ctk.CTkComboBox(
            location_wrap,
            values=deduped_locations,
            width=220,
            font=THEME.typography.body_md,
            command=self._handle_location_change,
        )
        self._location_dropdown.pack(side="left")
        style_secondary_dropdown(self._location_dropdown)

        if initial_location in deduped_locations:
            self._location_dropdown.set(initial_location)
        else:
            self._location_dropdown.set(deduped_locations[0])

    def get_selected_location(self) -> str:
        """Return currently selected location context."""
        if self._location_dropdown is None:
            return ""
        return self._location_dropdown.get()

    def select_tab(self, tab_key: str, invoke_callback: bool = True):
        """Select and highlight a tab key, then invoke callback."""
        if tab_key not in self._tab_buttons:
            return

        self._active_tab_key = tab_key
        for key in self._tab_buttons:
            self._set_tab_style(key, is_active=(key == tab_key))

        if invoke_callback and self._on_tab_selected is not None:
            self._on_tab_selected(tab_key, self.get_selected_location())

    def _handle_location_change(self, selected_location: str):
        if self._on_location_changed is None or not self._active_tab_key:
            return
        self._on_location_changed(self._active_tab_key, selected_location)

    def _set_tab_style(self, tab_key: str, is_active: bool):
        button = self._tab_buttons[tab_key]
        if is_active:
            button.configure(
                fg_color=(THEME.colors.primary_blue, THEME.colors.primary_blue),
                hover_color=(THEME.colors.primary_blue_hover, THEME.colors.primary_blue_hover),
                text_color=("white", "white"),
            )
        else:
            button.configure(
                fg_color=THEME.colors.secondary_gray,
                hover_color=THEME.colors.secondary_gray_hover,
                text_color=THEME.colors.text,
            )
