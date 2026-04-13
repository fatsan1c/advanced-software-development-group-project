"""
Contributors: Ahmed AlShamy (24045361)

Data table UI components for displaying and managing tabular data.

This module provides class-based table building functionality including:
- DataTable: Full-featured table with CRUD operations and pagination
- TablePopupWithHeader: Shared popup table wiring with optional header controls
- EditableTablePopup: Standardized edit popup with optional location filter
- ViewableTablePopup: Standardized read-only popup table
"""

import inspect

import customtkinter as ctk

import pages.components.input_validation as input_validation
from pages.components.config.theme import THEME
from pages.components.ui_controls_utils import (
    create_debounced_refresh,
    normalize_location_value,
    create_popup_header_with_location,
    create_refresh_button,
    vertical_divider,
)


class DataTable:
    """Build and manage data tables with optional CRUD behavior."""

    def __init__(
        self,
        parent,
        columns,
        data=None,
        editable=False,
        deletable=False,
        on_update=None,
        on_delete=None,
        refresh_data=None,
        show_refresh_button: bool = True,
        render_batch_size: int = 0,
        page_size: int = 0,
    ):
        from .ui_containers import ScrollableContainer

        self.parent = parent
        self.columns = columns
        self.data = data
        self.editable = editable
        self.deletable = deletable
        self.on_update = on_update
        self.on_delete = on_delete
        self.refresh_data = refresh_data
        self.show_refresh_button = show_refresh_button
        self.render_batch_size = int(render_batch_size or 0)
        self.page_size = int(page_size or 0)
        self.scrollable_container = ScrollableContainer

        self.table_container = ctk.CTkFrame(parent)
        self.table_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.error_label = ctk.CTkLabel(
            self.table_container,
            text="",
            font=("Arial", 12),
            text_color="red",
            wraplength=600,
        )

        self.content_ref = {"content": None}
        self.pagination_ref = {"page": 1, "total_pages": 1}

        def refresh_table():
            self._refresh_table_impl()

        self.refresh_table = refresh_table

        def _set_page(p: int):
            self.pagination_ref["page"] = int(p)
            self.refresh_table()

        def _reset_page():
            self.pagination_ref["page"] = 1

        self.refresh_table.set_page = _set_page  # type: ignore[attr-defined]
        self.refresh_table.reset_page = _reset_page  # type: ignore[attr-defined]

        self.refresh_table()

    def _refresh_table_impl(self):
        self.error_label.pack_forget()

        current_data = self.refresh_data() if self.refresh_data else self.data or []
        total_rows = len(current_data)

        if self.content_ref["content"] is None:
            content = self.scrollable_container(
                self.table_container,
                pady=0,
                padx=0,
                hide_scrollbar_when_loading=True,
            )
            self.content_ref["content"] = content
        else:
            for widget in self.content_ref["content"].winfo_children():
                widget.destroy()
            content = self.content_ref["content"]

        header_row = ctk.CTkFrame(content, fg_color=THEME.colors.secondary_gray)
        header_row.pack(fill="x", padx=5, pady=(5, 0))

        for col in self.columns:
            col_width = col.get("width", 150)
            header_cell = ctk.CTkLabel(
                header_row,
                text=col["name"],
                width=col_width - 10,
                font=("Arial", 13, "bold"),
                anchor="w",
            )
            header_cell.pack(side="left", padx=5, pady=8)
            if col != self.columns[-1]:
                vertical_divider(header_row, padx=(0, 8))

        if self.editable or self.deletable:
            vertical_divider(header_row, padx=(0, 8))
            ctk.CTkLabel(
                header_row,
                text="Actions",
                width=120,
                font=("Arial", 13, "bold"),
                anchor="center",
            ).pack(side="right", padx=5, pady=8)

        if total_rows == 0:
            empty_label = ctk.CTkLabel(
                content,
                text="No data available",
                font=("Arial", 14),
                text_color=THEME.colors.disabled_text,
            )
            empty_label.pack(pady=20)
            return

        if self.page_size > 0:
            total_pages = max(1, (total_rows + self.page_size - 1) // self.page_size)
            self.pagination_ref["total_pages"] = total_pages
            self.pagination_ref["page"] = max(1, min(int(self.pagination_ref["page"]), total_pages))
            start = (self.pagination_ref["page"] - 1) * self.page_size
            end = start + self.page_size
            page_data = current_data[start:end]
        else:
            self.pagination_ref["total_pages"] = 1
            self.pagination_ref["page"] = 1
            page_data = current_data

        batch_size = self.render_batch_size if self.render_batch_size > 0 else 0

        loading_label = None
        if batch_size and len(page_data) > batch_size:
            loading_label = ctk.CTkLabel(
                content,
                text=f"Loading {len(page_data)} rows...",
                font=("Arial", 12),
                text_color=THEME.colors.text,
            )
            loading_label.pack(anchor="w", padx=5, pady=(8, 2))

        def finalize_controls():
            if loading_label:
                loading_label.destroy()

            pager = None
            has_page_navigation = self.page_size > 0 and total_rows > self.page_size
            
            if has_page_navigation or self.show_refresh_button:
                pager = ctk.CTkFrame(content, fg_color="transparent")
                pager.pack(fill="x", pady=(10, 0), padx=5)

            if has_page_navigation:

                def set_page(p: int):
                    self.pagination_ref["page"] = p
                    self.refresh_table()

                prev_btn = ctk.CTkButton(
                    pager,
                    text="← Prev",
                    width=90,
                    height=32,
                    command=lambda: set_page(max(1, self.pagination_ref["page"] - 1)),
                    state="normal" if self.pagination_ref["page"] > 1 else "disabled",
                    fg_color=THEME.colors.secondary_gray,
                    hover_color=THEME.colors.secondary_gray_hover,
                    text_color=THEME.colors.text,
                    text_color_disabled=THEME.colors.disabled_text,
                )
                prev_btn.pack(side="left")

                page_btn_frame = ctk.CTkFrame(pager, fg_color="transparent")
                page_btn_frame.pack(side="left", padx=10)

                cur = self.pagination_ref["page"]
                total = self.pagination_ref["total_pages"]

                def add_page_button(label, page_num=None, disabled=False):
                    btn = ctk.CTkButton(
                        page_btn_frame,
                        text=str(label),
                        width=38,
                        height=32,
                        command=(lambda p=page_num: set_page(p)) if page_num else None,
                        state="disabled" if disabled else "normal",
                        fg_color=THEME.colors.secondary_gray,
                        hover_color=THEME.colors.secondary_gray_hover,
                        text_color=THEME.colors.text,
                        text_color_disabled=THEME.colors.disabled_text,
                    )
                    btn.pack(side="left", padx=2)

                window = 2
                pages = [1]
                for p in range(max(2, cur - window), min(total, cur + window) + 1):
                    pages.append(p)
                if total not in pages:
                    pages.append(total)

                last = None
                for p in pages:
                    if last is not None and p - last > 1:
                        add_page_button("...", disabled=True)
                    add_page_button(p, page_num=p, disabled=(p == cur))
                    last = p

                next_btn = ctk.CTkButton(
                    pager,
                    text="Next →",
                    width=90,
                    height=32,
                    command=lambda: set_page(min(total, self.pagination_ref["page"] + 1)),
                    state="normal" if self.pagination_ref["page"] < total else "disabled",
                    fg_color=THEME.colors.secondary_gray,
                    hover_color=THEME.colors.secondary_gray_hover,
                    text_color=THEME.colors.text,
                    text_color_disabled=THEME.colors.disabled_text,
                )
                next_btn.pack(side="left", padx=(10, 0))

                ctk.CTkLabel(
                    pager,
                    text=f"Page {cur} / {total} ({total_rows} rows)",
                    font=("Arial", 12),
                    text_color=THEME.colors.text,
                ).pack(side="right")

            if self.show_refresh_button and pager is not None:
                refresh_btn = create_refresh_button(
                    pager,
                    self.refresh_table,
                    padx=25 if has_page_navigation else 0,
                )
                if has_page_navigation:
                    refresh_btn.pack_configure(side="left")
                else:
                    refresh_btn.pack_configure(side="top", anchor="center")

        def render_rows_range(start_idx: int):
            end_idx = len(page_data) if not batch_size else min(start_idx + batch_size, len(page_data))
            for row_data in page_data[start_idx:end_idx]:
                self._create_row_widget(
                    parent_widget=content,
                    row_data=row_data,
                )

            if end_idx < len(page_data):
                self.table_container.after(1, lambda: render_rows_range(end_idx))
            else:
                finalize_controls()

        if batch_size:
            render_rows_range(0)
        else:
            for row_data in page_data:
                self._create_row_widget(parent_widget=content, row_data=row_data)
            finalize_controls()

    def _create_row_widget(self, parent_widget, row_data):
        row = ctk.CTkFrame(parent_widget, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=2)

        cell_widgets = {}

        for col in self.columns:
            col_width = col.get("width", 150)
            col_key = col["key"]
            col_editable = col.get("editable", True)
            raw_value = row_data.get(col_key, "")

            value = raw_value
            col_format = col.get("format")
            if col_format == "currency":
                value = input_validation.format_currency_display(raw_value)
            elif col_format == "boolean":
                options = col.get("options", ["True", "False"])
                try:
                    value = options[0] if int(raw_value) == 1 else options[1]
                except (ValueError, TypeError, IndexError):
                    value = str(raw_value)
            else:
                value = str(raw_value)
                if col.get("prefix") and value:
                    value = f"{col['prefix']}{value}"
                if col.get("suffix") and value:
                    value = f"{value}{col['suffix']}"

            cell_frame = ctk.CTkFrame(row, fg_color="transparent")
            cell_frame.pack(side="left", padx=5, pady=5)

            cell_label = ctk.CTkLabel(
                cell_frame,
                text=value,
                width=col_width,
                anchor="w",
                font=("Arial", 12),
            )
            cell_label.pack()

            cell_widgets[col_key] = {"label": cell_label, "editable": col_editable}

        if self.editable or self.deletable:
            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.pack(side="right", padx=5)

            if self.editable:
                edit_btn = ctk.CTkButton(
                    action_frame,
                    text="Edit",
                    width=50,
                    height=28,
                    command=lambda: self._edit_row(row_data, cell_widgets),
                    fg_color=THEME.colors.secondary_gray,
                    hover_color=THEME.colors.secondary_gray_hover,
                    text_color=THEME.colors.text,
                )
                edit_btn.pack(side="left", padx=2)

            if self.deletable:
                delete_btn = ctk.CTkButton(
                    action_frame,
                    text="Delete",
                    width=60,
                    height=28,
                    command=lambda: self._delete_row(row_data),
                    fg_color=("red", "darkred"),
                    hover_color=("darkred", "red"),
                )
                delete_btn.pack(side="left", padx=2)

    def _edit_row(self, row_data, cell_widgets):
        self.error_label.pack_forget()
        edit_data = {}

        for col in self.columns:
            col_key = col["key"]
            if col_key in cell_widgets and cell_widgets[col_key]["editable"]:
                widget_info = cell_widgets[col_key]
                label = widget_info["label"]
                current_value = label.cget("text")
                col_format = col.get("format")

                if col_format == "currency" and isinstance(current_value, str):
                    current_value = input_validation.strip_currency_formatting(current_value)

                label.pack_forget()

                if col_format == "dropdown":
                    options = col.get("options", [])
                    dropdown = ctk.CTkOptionMenu(
                        label.master,
                        values=options if options else ["No options"],
                        width=col.get("width", 150),
                        height=28,
                        font=("Arial", 12),
                    )

                    if current_value and options and current_value in options:
                        dropdown.set(current_value)
                    elif options:
                        dropdown.set(options[0])

                    dropdown.pack()
                    edit_data[col_key] = dropdown

                elif col_format == "boolean":
                    options = col.get("options", ["True", "False"])

                    dropdown = ctk.CTkOptionMenu(
                        label.master,
                        values=options,
                        width=col.get("width", 150),
                        height=28,
                        font=("Arial", 12),
                    )
                    if current_value in options:
                        dropdown.set(current_value)
                    else:
                        dropdown.set(options[0])
                    dropdown.pack()
                    edit_data[col_key] = {"widget": dropdown, "boolean_options": options}

                else:
                    entry = ctk.CTkEntry(
                        label.master,
                        width=col.get("width", 150),
                        font=("Arial", 12),
                    )

                    if col_format == "number":
                        vcmd = (entry.register(input_validation.validate_number_input), "%P")
                        entry.configure(validate="key", validatecommand=vcmd)
                    elif col_format == "currency":
                        vcmd = (entry.register(input_validation.validate_currency_input), "%P")
                        entry.configure(validate="key", validatecommand=vcmd)
                    elif col_format == "date":
                        vcmd = (entry.register(input_validation.validate_date_input), "%P")
                        entry.configure(validate="key", validatecommand=vcmd)
                        entry.configure(placeholder_text="YYYY-MM-DD")

                    entry.insert(0, current_value)
                    entry.pack()
                    edit_data[col_key] = entry

        if cell_widgets:
            first_cell = list(cell_widgets.values())[0]
            button_frame = first_cell["label"].master.master

            for widget in button_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for btn in widget.winfo_children():
                        if isinstance(btn, ctk.CTkButton):
                            if btn.cget("text") == "Edit":
                                btn.configure(
                                    text="Save",
                                    command=lambda: self._save_row(row_data, edit_data),
                                )
                            elif btn.cget("text") == "Delete":
                                btn.configure(
                                    text="Cancel",
                                    command=lambda: self.refresh_table(),
                                    fg_color=THEME.colors.secondary_gray,
                                    hover_color=THEME.colors.secondary_gray_hover,
                                    text_color=THEME.colors.text,
                                )

    def _save_row(self, row_data, edit_data):
        self.error_label.pack_forget()
        updated_data = {}
        for key, item in edit_data.items():
            if isinstance(item, dict) and "widget" in item:
                widget = item["widget"]
                selected_label = widget.get()

                if "boolean_options" in item:
                    boolean_options = item["boolean_options"]
                    updated_data[key] = 1 if selected_label == boolean_options[0] else 0
                elif "value_map" in item:
                    value_map = item["value_map"]
                    updated_data[key] = value_map.get(selected_label, selected_label)
                else:
                    updated_data[key] = selected_label
            elif isinstance(item, ctk.CTkOptionMenu):
                updated_data[key] = item.get()
            else:
                updated_data[key] = item.get()

        if self.on_update:
            result = self.on_update(row_data, updated_data)
            if result is True:
                self.refresh_table()
            else:
                error_message = str(result) if result else "Update failed"
                self.error_label.configure(text=f"Update failed: {error_message}")
                self.error_label.pack(fill="x", padx=10, pady=(5, 0))

    def _delete_row(self, row_data):
        self.error_label.pack_forget()

        if self.on_delete:
            result = self.on_delete(row_data)
            if result is True:
                self.refresh_table()
            else:
                error_message = str(result) if result else "Delete failed"
                self.error_label.configure(text=f"Delete failed: {error_message}")
                self.error_label.pack(fill="x", padx=10, pady=(5, 0))


class TablePopupWithHeader:
    """Shared popup table builder with optional location header controls."""

    @staticmethod
    def _accepts_location_argument(func) -> bool:
        try:
            signature = inspect.signature(func)
        except (TypeError, ValueError):
            return False

        for param in signature.parameters.values():
            if param.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            ):
                return True
        return False

    def __init__(
        self,
        popup_content,
        columns,
        get_data_func,
        include_location_filter=False,
        location_mapper=None,
        on_delete_func=None,
        on_update_func=None,
        editable=False,
        deletable=False,
    ):
        self.popup_content = popup_content
        self.columns = columns
        self.get_data_func = get_data_func
        self.on_delete_func = on_delete_func
        self.on_update_func = on_update_func
        self.include_location_filter = include_location_filter
        self.location_mapper = location_mapper
        self._get_data_accepts_location = self._accepts_location_argument(get_data_func)

        self.header = None
        self.location_dropdown = None

        if include_location_filter:
            self.header, self.location_dropdown = create_popup_header_with_location(popup_content)

        def table_data_loader():
            if not self.include_location_filter or self.location_dropdown is None:
                return self.get_data_func()

            raw_location = self.location_dropdown.get()
            if callable(self.location_mapper):
                selected_location = self.location_mapper(raw_location)
            else:
                selected_location = normalize_location_value(raw_location)

            if self._get_data_accepts_location:
                return self.get_data_func(selected_location)
            return self.get_data_func()

        self.table = DataTable(
            popup_content,
            columns,
            editable=editable,
            deletable=deletable,
            refresh_data=table_data_loader,
            on_delete=on_delete_func,
            on_update=on_update_func,
            show_refresh_button=not include_location_filter, # Put refresh button in header if location filter is included, otherwise show it in table controls
            render_batch_size=20,
            page_size=10,
        )

        if include_location_filter and self.header is not None:
            create_refresh_button(self.header, self.table.refresh_table)

        if self.location_dropdown is not None:
            def refresh_with_reset(_choice=None):
                if hasattr(self.table.refresh_table, "reset_page"):
                    self.table.refresh_table.reset_page()
                self.table.refresh_table()

            self._refresh_timer, schedule_refresh = create_debounced_refresh(
                popup_content,
                refresh_with_reset,
            )
            self.location_dropdown.configure(command=schedule_refresh)


class EditableTablePopup(TablePopupWithHeader):
    """Build standardized edit popups with data tables."""

    def __init__(
        self,
        popup_content,
        columns,
        get_data_func,
        on_delete_func,
        on_update_func,
        include_location_filter=False,
        location_mapper=None,
        deletable=True,
    ):
        super().__init__(
            popup_content=popup_content,
            columns=columns,
            get_data_func=get_data_func,
            include_location_filter=include_location_filter,
            location_mapper=location_mapper,
            on_delete_func=on_delete_func,
            on_update_func=on_update_func,
            editable=True,
            deletable=deletable,
        )


class ViewableTablePopup(TablePopupWithHeader):
    """Build standardized read-only popups with data tables."""

    def __init__(
        self,
        popup_content,
        columns,
        get_data_func,
        include_location_filter=False,
        location_mapper=None,
    ):
        super().__init__(
            popup_content=popup_content,
            columns=columns,
            get_data_func=get_data_func,
            include_location_filter=include_location_filter,
            location_mapper=location_mapper,
            on_delete_func=None,
            on_update_func=None,
            editable=False,
            deletable=False,
        )
