"""
Contributors: Aaron Antal-Bento (23013693), Ahmed AlShamy (24045361)

Form UI components for data entry and user input.

This module provides comprehensive form building functionality including:
- Field types: text, dropdown, checkbox
- Subtypes: text, number, password, currency, date
- Integrated date picker with tkcalendar
- Built-in validation and error handling
"""

import customtkinter as ctk
from pages.components.config.theme import THEME
import pages.components.input_validation as input_validation
from pages.components.date_utils import open_date_picker
from pages.components.style_utils import style_primary_dropdown
from pages.components.ui_controls_utils import create_dynamic_dropdown_with_refresh


class Form:
    """Builds and manages a themed form with validation and submission flow."""

    def __init__(
        self,
        parent,
        fields,
        name="",
        submit_text="Submit",
        on_submit=None,
        field_per_row=2,
    ):
        self.parent = parent
        self.fields = fields
        self.name = name
        self.submit_text = submit_text
        self.on_submit = on_submit
        self.field_per_row = field_per_row

        self.input_height = 28
        self.input_font_size = 11
        self.button_height = 40
        self.button_font_size = 15
        self.row_pady = 3

        self.form = None
        self.error_label = None
        self.success_label = None
        self.field_widgets = {}
        self.dynamic_dropdown_refreshers = {}
        self.dynamic_dropdown_maps = {}

        # Standardized pattern: construction creates the component immediately.
        self.form = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.form.pack(fill="x", expand=False, pady=5)

        self._create_title()
        self._create_fields()
        self._create_message_labels()
        self._create_submit_button()

    def _create_title(self):
        if self.name:
            ctk.CTkLabel(
                self.form,
                text=self.name,
                font=("Arial", 13, "bold"),
                anchor="w",
            ).pack(padx=5, pady=0)

    def _create_fields(self):
        fields_count = 0
        current_row = None

        for field in self.fields:
            if fields_count % self.field_per_row == 0:
                current_row = ctk.CTkFrame(self.form, fg_color="transparent")
                current_row.pack(fill="x", pady=self.row_pady, padx=5)

            field_name = field["name"]
            field_type = field.get("type", "text")
            field_subtype = field.get("subtype", "text")
            field_default = field.get("default", "")
            field_required = field.get("required", False)
            small_field = field.get("small", False)

            field_frame = ctk.CTkFrame(current_row, fg_color="transparent")
            field_frame.pack(
                fill="x" if not small_field else None,
                padx=5,
                side="left",
                expand=not small_field,
            )

            if field.get("show_label", True):
                ctk.CTkLabel(
                    field_frame,
                    text=field_name + ("*" if field_required else ""),
                    font=("Arial", self.input_font_size),
                    height=1,
                ).pack(anchor="w", pady=(0, 2), padx=(3, 0))

            widget = self._create_field_widget(field_frame, field, field_type, field_subtype)
            self._apply_default_value(widget, field_default, field_type, field_subtype, field)

            self.field_widgets[field_name] = {
                "widget": widget,
                "type": field_type,
                "subtype": field_subtype,
                "required": field_required,
            }
            fields_count += 1

    def _create_field_widget(self, field_frame, field, field_type, field_subtype):
        if field_type == "text":
            return self._create_text_widget(field_frame, field, field_subtype)

        if field_type == "dropdown":
            return self._create_dropdown_widget(field_frame, field, field_subtype)

        if field_type == "checkbox":
            return self._create_checkbox_widget(field_frame)

        return ctk.CTkEntry(field_frame)

    def _create_text_widget(self, field_frame, field, field_subtype):
        entry_kwargs = {
            "placeholder_text": field.get("placeholder", None),
            "height": self.input_height,
            "font": ("Arial", self.input_font_size),
            "corner_radius": THEME.radii.input,
        }
        widget = ctk.CTkEntry(field_frame, **entry_kwargs)

        if field_subtype == "password":
            widget.configure(show="•")

        elif field_subtype == "number":
            vcmd = (widget.register(input_validation.validate_number_input), "%P")
            widget.configure(validate="key", validatecommand=vcmd, require_redraw=True)
            self._bind_placeholder_on_focusout(widget)

        elif field_subtype == "currency":
            vcmd = (widget.register(input_validation.validate_currency_input), "%P")
            widget.configure(validate="key", validatecommand=vcmd)
            self._bind_placeholder_on_focusout(widget)

        elif field_subtype == "date":
            return self._create_date_widget(field_frame, entry_kwargs)

        widget.pack(fill="x")
        return widget

    def _create_date_widget(self, field_frame, entry_kwargs):
        date_row = ctk.CTkFrame(field_frame, fg_color="transparent")
        date_row.pack(fill="x", expand=True)

        entry_kwargs["width"] = 140
        widget = ctk.CTkEntry(date_row, **entry_kwargs)
        vcmd = (widget.register(input_validation.validate_date_input), "%P")
        widget.configure(validate="key", validatecommand=vcmd)
        widget.pack(side="left", fill="x", expand=True)

        def open_calendar(target_widget=widget):
            open_date_picker(target_widget, self.parent.winfo_toplevel())

        ctk.CTkButton(
            date_row,
            text="📅",
            width=30,
            height=30,
            font=("Arial", 13),
            command=open_calendar,
            fg_color=THEME.colors.secondary_gray,
            hover_color=THEME.colors.secondary_gray_hover,
            text_color=THEME.colors.text,
        ).pack(side="left", padx=(6, 0))

        self._bind_placeholder_on_focusout(widget)
        return widget

    def _create_dropdown_widget(self, field_frame, field, field_subtype):
        if field_subtype == "dynamic":
            options_config = field.get("options", {})
            data_fetcher = options_config.get("data_fetcher")
            display_formatter = options_config.get("display_formatter", lambda x: (str(x), x))
            empty_message = options_config.get("empty_message", "No items available")

            widget, data_map, refresh_func = create_dynamic_dropdown_with_refresh(
                parent=field_frame,
                data_fetcher=data_fetcher,
                display_formatter=display_formatter,
                empty_message=empty_message,
            )
            self.dynamic_dropdown_maps[field["name"]] = data_map
            self.dynamic_dropdown_refreshers[field["name"]] = refresh_func
            return widget

        options = field.get("options", [])
        widget = ctk.CTkOptionMenu(
            field_frame,
            values=options,
            height=self.input_height,
            font=("Arial", self.input_font_size),
        )
        style_primary_dropdown(widget)
        widget.pack(fill="x")
        return widget

    def _create_checkbox_widget(self, field_frame):
        widget = ctk.CTkCheckBox(
            field_frame,
            text="",
            font=("Arial", self.input_font_size),
        )
        widget.pack(anchor="w")
        return widget

    def _apply_default_value(self, widget, default_value, field_type, field_subtype, field):
        if field_type == "text" and default_value:
            widget.insert(0, str(default_value))
            return

        if field_type == "checkbox" and default_value:
            widget.select()
            return

        if field_type == "dropdown" and field_subtype != "dynamic":
            options = field.get("options", [])
            if default_value and default_value in options:
                widget.set(default_value)
            elif options:
                widget.set(options[0])

    @staticmethod
    def _bind_placeholder_on_focusout(widget):
        def on_focusout(_event, w=widget):
            if not w.get():
                w.configure(validate="none")
                w.delete(0, "end")
                w.configure(validate="key")

        widget.bind("<FocusOut>", on_focusout)

    def _create_message_labels(self):
        self.error_label = ctk.CTkLabel(
            self.form,
            text="",
            font=("Arial", 12),
            text_color="red",
            wraplength=400,
        )

        self.success_label = ctk.CTkLabel(
            self.form,
            text="",
            font=("Arial", 12),
            text_color="green",
            wraplength=400,
        )

    def _create_submit_button(self):
        submit_button = ctk.CTkButton(
            self.form,
            text=self.submit_text,
            command=self._handle_submit,
            height=self.button_height,
            font=("Arial", self.button_font_size, "bold"),
            corner_radius=THEME.radii.button,
            fg_color=(THEME.colors.primary_blue, THEME.colors.primary_blue),
            hover_color=(THEME.colors.primary_blue_hover, THEME.colors.primary_blue_hover),
            text_color=("white", "white"),
        )
        submit_button.pack(pady=(10, 5), padx=10, fill="x")

    def _collect_values(self):
        values = {}
        for field_name, field_info in self.field_widgets.items():
            widget = field_info["widget"]
            field_type = field_info["type"]
            required = field_info["required"]

            if field_type == "text":
                value = widget.get().strip()
            elif field_type == "dropdown":
                display_value = widget.get()
                if field_name in self.dynamic_dropdown_maps:
                    value = self.dynamic_dropdown_maps[field_name].get(display_value, display_value)
                else:
                    value = display_value
            elif field_type == "checkbox":
                value = widget.get() == 1
            else:
                value = None

            if required and (value == "" or value is None):
                self.error_label.configure(text=f"Error: {field_name} is required")
                self.error_label.pack(pady=0, padx=10)
                return None

            values[field_name] = value

        return values

    def _refresh_dynamic_dropdowns(self):
        for refresh_func in self.dynamic_dropdown_refreshers.values():
            refresh_func()

    def _clear_fields_after_success(self):
        for field_name, field_info in self.field_widgets.items():
            widget = field_info["widget"]
            field_type = field_info["type"]
            sub_type = field_info.get("subtype", None)

            if field_type == "text":
                widget.delete(0, "end")
            elif field_type == "checkbox":
                widget.deselect()
            elif field_type == "dropdown" and sub_type != "dynamic":
                field_def = next((f for f in self.fields if f["name"] == field_name), None)
                if field_def:
                    options = field_def.get("options", [])
                    if options and isinstance(options, list):
                        widget.set(options[0])

    def _handle_submit(self):
        self.error_label.pack_forget()
        self.success_label.pack_forget()

        values = self._collect_values()
        if values is None or not self.on_submit:
            return

        result = self.on_submit(values)

        if isinstance(result, str):
            self.error_label.configure(text=result)
            self.error_label.pack(pady=0, padx=10)
            self.form.after(50, self._refresh_dynamic_dropdowns)
        elif result is True:
            self.success_label.configure(text="Operation completed successfully.")
            self.success_label.pack(pady=0, padx=10)
            self.form.after(50, self._refresh_dynamic_dropdowns)
            self._clear_fields_after_success()
