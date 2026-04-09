"""Contributors: Aaron Antal-Bento (23013693)

Drop-in CTkOptionMenu replacement with a ttk-like scrollable popup list."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional

import customtkinter as ctk
from customtkinter import ThemeManager
from pages.components.config.theme import THEME


class _ScrollableDropdownPopup:
    """Popup list window used by ScrollableCTkOptionMenu."""

    def __init__(
        self,
        parent: tk.Widget,
        on_select: Callable[[str], None],
        max_visible_rows: int = 10,
        fit_content_width: bool = True,
        min_content_width: int = 120,
        show_scrollbar: bool = False,
        min_character_width: int = 18,
    ) -> None:
        self._parent = parent
        self._on_select = on_select
        self._max_visible_rows = max(3, int(max_visible_rows))
        self._fit_content_width = bool(fit_content_width)
        self._min_content_width = max(80, int(min_content_width))
        self._show_scrollbar = bool(show_scrollbar)
        self._min_character_width = max(6, int(min_character_width))

        self._window: Optional[tk.Toplevel] = None
        self._frame: Optional[tk.Frame] = None
        self._listbox: Optional[tk.Listbox] = None
        self._scrollbar: Optional[tk.Scrollbar] = None
        self._raw_values: list[str] = []

    @staticmethod
    def _safe_configure(widget, **kwargs) -> None:
        """Configure widget keys defensively across Tk variants."""
        for key, value in kwargs.items():
            try:
                widget.configure(**{key: value})
            except Exception:
                # Some Tk builds/themes do not support every color option.
                pass

    @staticmethod
    def _current_mode() -> str:
        return str(ctk.get_appearance_mode()).lower()

    def show(
        self,
        values: list[str],
        current_value: str,
        x: int,
        y: int,
        width_px: int,
        font_config: tuple | ctk.CTkFont | None = None,
    ) -> None:
        if not values:
            return

        self._ensure_widgets()
        assert self._window is not None
        assert self._listbox is not None

        self._listbox.delete(0, tk.END)
        self._raw_values = list(values)
        for value in values:
            self._listbox.insert(tk.END, str(value).ljust(self._min_character_width))

        list_font = self._resolve_tk_font(font_config)
        self._listbox.configure(font=list_font)

        self._apply_style()

        row_height = max(18, list_font.metrics("linespace") + 6)
        visible_rows = min(len(values), self._max_visible_rows)
        height_px = (visible_rows * row_height) + 4
        self._set_scrollbar_visibility(len(values) > visible_rows)
        popup_width = self._calculate_popup_width(values, list_font, width_px)

        try:
            selected_index = values.index(current_value)
        except ValueError:
            selected_index = 0

        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(selected_index)
        self._listbox.activate(selected_index)
        self._listbox.see(selected_index)

        self._window.geometry(f"{popup_width}x{max(36, height_px)}+{x}+{y}")
        self._window.deiconify()
        self._window.lift()
        self._window.focus_force()
        self._listbox.focus_set()

    def hide(self) -> None:
        if self._window is None:
            return

        self._window.withdraw()

    def destroy(self) -> None:
        if self._window is not None:
            try:
                self._window.destroy()
            except Exception:
                pass

        self._window = None
        self._frame = None
        self._listbox = None
        self._scrollbar = None

    def _ensure_widgets(self) -> None:
        if self._window is not None:
            return

        self._window = tk.Toplevel(self._parent)
        self._window.withdraw()
        self._window.overrideredirect(True)
        self._window.resizable(False, False)
        self._window.transient(self._parent.winfo_toplevel())

        self._frame = tk.Frame(self._window, bd=0, relief="flat")
        # Keep a 2px margin so the toplevel background acts as a thicker border.
        self._frame.pack(fill="both", expand=True, padx=2, pady=2)

        self._listbox = tk.Listbox(
            self._frame,
            activestyle="none",
            selectmode="browse",
            exportselection=False,
            highlightthickness=0,
            relief="flat",
            borderwidth=0,
            takefocus=True,
        )
        self._listbox.pack(side="left", fill="both", expand=True, padx=(4, 0))

        self._scrollbar = tk.Scrollbar(self._frame, orient="vertical", command=self._listbox.yview)
        self._scrollbar.pack(side="right", fill="y")
        self._listbox.configure(yscrollcommand=self._scrollbar.set)

        self._listbox.bind("<ButtonRelease-1>", self._select_from_pointer)
        self._listbox.bind("<Double-Button-1>", self._select_from_pointer)
        self._listbox.bind("<Return>", self._select_active)
        self._listbox.bind("<KP_Enter>", self._select_active)
        self._listbox.bind("<Escape>", self._hide_event)

        self._listbox.bind("<MouseWheel>", self._on_mouse_wheel)
        self._listbox.bind("<Button-4>", self._on_mouse_wheel)
        self._listbox.bind("<Button-5>", self._on_mouse_wheel)
        self._listbox.bind("<Motion>", self._on_motion)

        # Focus transfer from the owner to the popup should not close immediately.
        self._window.bind("<FocusOut>", self._on_focus_out)

    def _set_scrollbar_visibility(self, needs_scrollbar: bool) -> None:
        if self._scrollbar is None:
            return

        if self._show_scrollbar and needs_scrollbar:
            self._scrollbar.pack(side="right", fill="y")
        else:
            self._scrollbar.pack_forget()

    def _resolve_color(self, color_value, fallback: str = "#FFFFFF") -> str:
        if color_value is None:
            return fallback

        if isinstance(color_value, (tuple, list)):
            try:
                # Resolve tuple based on current appearance mode if available.
                apply_mode = getattr(self._parent, "_apply_appearance_mode", None)
                if callable(apply_mode):
                    return apply_mode(color_value)
                mode = self._current_mode()
                return color_value[1] if mode == "dark" else color_value[0]
            except Exception:
                return color_value[0]

        if isinstance(color_value, str):
            color_str = color_value.strip()

            # CustomTkinter can expose dual-mode colors as "<light> <dark>" strings.
            # Tk expects one color token, so resolve by current appearance mode.
            if " " in color_str and color_str.startswith("#"):
                parts = color_str.split()
                if len(parts) >= 2 and parts[0].startswith("#") and parts[1].startswith("#"):
                    mode = self._current_mode()
                    return parts[1] if mode == "dark" else parts[0]

            return color_str

        return color_value

    def _apply_style(self) -> None:
        if self._window is None or self._frame is None or self._listbox is None or self._scrollbar is None:
            return

        dropdown_theme = ThemeManager.theme.get("DropdownMenu", {})
        theme_fg = dropdown_theme.get("fg_color", ("gray90", "gray20"))
        theme_hover = dropdown_theme.get("hover_color", ("gray75", "gray28"))
        theme_text = dropdown_theme.get("text_color", ("gray10", "gray90"))

        try:
            dropdown_fg_source = self._parent.cget("dropdown_fg_color")
        except Exception:
            dropdown_fg_source = theme_fg
        try:
            dropdown_hover_source = self._parent.cget("dropdown_hover_color")
        except Exception:
            dropdown_hover_source = theme_hover
        try:
            dropdown_text_source = self._parent.cget("dropdown_text_color")
        except Exception:
            dropdown_text_source = theme_text

        dropdown_fg = self._resolve_color(dropdown_fg_source, self._resolve_color(theme_fg, "#F5F5F5"))
        dropdown_hover = self._resolve_color(dropdown_hover_source, self._resolve_color(theme_hover, "#D9D9D9"))
        dropdown_text = self._resolve_color(dropdown_text_source, self._resolve_color(theme_text, "#1F1F1F"))

        # Use a fixed white border for strong visual separation.
        border_color = "#FFFFFF"

        self._safe_configure(self._window, bg=border_color)
        self._safe_configure(self._frame, bg=dropdown_fg, highlightthickness=0, bd=0)

        cursor = "hand2" if (sys.platform.startswith("win") or sys.platform == "darwin") else "arrow"

        self._safe_configure(
            self._listbox,
            bg=dropdown_fg,
            fg=dropdown_text,
            selectbackground=dropdown_hover,
            selectforeground=dropdown_text,
            highlightbackground=dropdown_fg,
            highlightcolor=dropdown_fg,
            disabledforeground=dropdown_text,
            cursor=cursor,
            selectborderwidth=0,
        )

        self._safe_configure(
            self._scrollbar,
            bg=dropdown_hover,
            troughcolor=dropdown_fg,
            activebackground=dropdown_hover,
            highlightbackground=dropdown_fg,
            relief="flat",
            bd=0,
        )

    def _calculate_popup_width(self, values: list[str], list_font: tkfont.Font, owner_width: int) -> int:
        popup_width = max(self._min_content_width, int(owner_width))

        if self._fit_content_width:
            text_px = max((list_font.measure(str(v)) for v in values), default=0)
            # Horizontal paddings + border + optional scrollbar allowance.
            scrollbar_px = 18 if self._show_scrollbar else 0
            extra_px = 22
            popup_width = max(popup_width, text_px + scrollbar_px + extra_px)

        # Keep popup on-screen even when very long values are present.
        try:
            screen_width = int(self._parent.winfo_screenwidth())
            max_width = max(self._min_content_width, screen_width - 24)
            popup_width = min(popup_width, max_width)
        except Exception:
            pass

        return popup_width

    def _resolve_tk_font(self, font_config: tuple | ctk.CTkFont | None) -> tkfont.Font:
        if isinstance(font_config, ctk.CTkFont):
            return tkfont.Font(
                family=font_config.cget("family"),
                size=font_config.cget("size"),
                weight=font_config.cget("weight"),
                slant=font_config.cget("slant"),
                underline=font_config.cget("underline"),
                overstrike=font_config.cget("overstrike"),
            )

        if isinstance(font_config, tuple) and len(font_config) >= 2:
            return tkfont.Font(family=font_config[0], size=font_config[1])

        return tkfont.nametofont("TkDefaultFont")

    def _select_from_pointer(self, _event: tk.Event) -> str:
        return self._select_active(_event)

    def _select_active(self, _event: tk.Event) -> str:
        if self._listbox is None:
            return "break"

        selection = self._listbox.curselection()
        if not selection:
            return "break"

        idx = int(selection[0])
        if idx < 0 or idx >= len(self._raw_values):
            return "break"

        value = self._raw_values[idx]
        self.hide()
        self._on_select(value)
        return "break"

    def _hide_event(self, _event: tk.Event) -> str:
        self.hide()
        return "break"

    def _on_focus_out(self, _event: tk.Event) -> None:
        self.hide()

    def _on_mouse_wheel(self, event: tk.Event) -> str:
        if self._listbox is None:
            return "break"

        delta = getattr(event, "delta", 0)
        if delta > 0:
            direction = -1
        elif delta < 0:
            direction = 1
        else:
            # Linux wheel events
            event_num = getattr(event, "num", None)
            direction = -1 if event_num == 4 else 1 if event_num == 5 else 0

        if direction != 0:
            self._listbox.yview_scroll(direction, "units")

        return "break"

    def _on_motion(self, event: tk.Event) -> str:
        if self._listbox is None:
            return "break"

        idx = self._listbox.nearest(event.y)
        if idx >= 0:
            self._listbox.selection_clear(0, tk.END)
            self._listbox.selection_set(idx)
            self._listbox.activate(idx)
        return "break"


class ScrollableDropdown(ctk.CTkOptionMenu):
    """CTkOptionMenu drop-in replacement with scrollable popup list."""

    def __init__(
        self,
        *args,
        dropdown_max_visible_rows: int = 10,
        dropdown_fit_content_width: bool = True,
        dropdown_min_content_width: int = 120,
        dropdown_show_scrollbar: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._dropdown_popup = _ScrollableDropdownPopup(
            parent=self,
            on_select=self._dropdown_callback,
            max_visible_rows=dropdown_max_visible_rows,
            fit_content_width=dropdown_fit_content_width,
            min_content_width=dropdown_min_content_width,
            show_scrollbar=dropdown_show_scrollbar,
        )

        self.configure(corner_radius=THEME.radii.input)

    def _open_dropdown_menu(self) -> None:
        if self._state is tk.DISABLED:
            return

        values = list(self.cget("values") or [])
        if not values:
            return

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self._apply_widget_scaling(self._current_height)
        width = self.winfo_width()

        self._dropdown_popup.show(
            values=values,
            current_value=self.get(),
            x=int(x),
            y=int(y),
            width_px=int(width),
            font_config=self.cget("dropdown_font"),
        )

    def configure(self, require_redraw=False, **kwargs):
        if "dropdown_max_visible_rows" in kwargs:
            rows = kwargs.pop("dropdown_max_visible_rows")
            self._dropdown_popup._max_visible_rows = max(3, int(rows))

        if "dropdown_fit_content_width" in kwargs:
            fit_width = kwargs.pop("dropdown_fit_content_width")
            self._dropdown_popup._fit_content_width = bool(fit_width)

        if "dropdown_min_content_width" in kwargs:
            min_width = kwargs.pop("dropdown_min_content_width")
            self._dropdown_popup._min_content_width = max(80, int(min_width))

        if "dropdown_show_scrollbar" in kwargs:
            show_scrollbar = kwargs.pop("dropdown_show_scrollbar")
            self._dropdown_popup._show_scrollbar = bool(show_scrollbar)

        return super().configure(require_redraw=require_redraw, **kwargs)

    def cget(self, attribute_name: str):
        if attribute_name == "dropdown_max_visible_rows":
            return self._dropdown_popup._max_visible_rows
        if attribute_name == "dropdown_fit_content_width":
            return self._dropdown_popup._fit_content_width
        if attribute_name == "dropdown_min_content_width":
            return self._dropdown_popup._min_content_width
        if attribute_name == "dropdown_show_scrollbar":
            return self._dropdown_popup._show_scrollbar
        return super().cget(attribute_name)

    def destroy(self):
        try:
            self._dropdown_popup.destroy()
        except Exception:
            pass
        super().destroy()
