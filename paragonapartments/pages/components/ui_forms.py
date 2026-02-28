"""Form UI components for data entry and user input.

This module provides comprehensive form building functionality including:
- form_element: Complex form builder with multiple field types
- Field types: text, dropdown, checkbox
- Subtypes: text, number, password, currency, date
- Integrated date picker with tkcalendar
- Built-in validation and error handling
"""

import customtkinter as ctk
from datetime import datetime
from pages.components.config.theme import PRIMARY_BLUE, PRIMARY_BLUE_HOVER, ROUND_BTN, ROUND_INPUT
import pages.components.input_validation as input_validation
import pages.components.ui_utilities as ui_utils


def form_element(
    parent,
    fields,
    name="",
    submit_text="Submit",
    on_submit=None,
    field_per_row=2
):
    """Create a form with customizable fields and a submit button with theme styling.
    
    Args:
        parent: The parent container
        fields: List of field dictionaries with keys:
            - 'name': Field name/label (required)
            - 'type': Input type - 'text', 'dropdown', 'checkbox' (default: 'text')
            - 'subtype': Subtype for text fields - 'text', 'number', 'password', 'currency', 'date' (default: 'text')
            - 'options': List of options for dropdown (required if type='dropdown')
            - 'default': Default value
            - 'required': Whether field is required (default: False)
            - 'small': Use smaller sizing for compact forms (default: False)
        name: Form name/identifier (optional)
        submit_text: Text for the submit button
        on_submit: Callback function that receives dict of {field_name: value}.
                   Callback should return True for success, or error message string for failure.
        field_per_row: Number of fields per row (default: 2)
        submit_button_font_size: Font size for submit button (default: 13)
        
    Returns:
        Tuple of (form_container, error_label) - use error_label to show custom errors
        
    Example:
        def handle_submit(values):
            # Validation or processing
            if not values['Username']:
                return "Username cannot be empty"
            # Database operation
            if db_error:
                return "Failed to create account: Database error"
            return True  # Success
        
        fields = [
            {'name': 'Username', 'type': 'text', 'required': True},
            {'name': 'Role', 'type': 'dropdown', 'options': ['Admin', 'User'], 'default': 'User'}
        ]
        form, error_label = form_element(parent, fields, submit_text="Create Account", on_submit=handle_submit)
    """
    
    # Size settings based on small parameter
    input_height = 28
    input_font_size = 11
    button_height = 40
    button_font_size = 15
    row_pady = 3
    
    form = ctk.CTkFrame(parent, fg_color="transparent")
    form.pack(fill="x", expand=False, pady=5)

    if name:
        ctk.CTkLabel(
            form,
            text=name,
            font=("Arial", 13),
            anchor="w"
        ).pack(padx=5, pady=0)
    
    # Store field widgets for retrieval
    field_widgets = {}

    fields_count = 0
    current_row = None

    for field in fields:
        if fields_count % field_per_row == 0:
            current_row = ctk.CTkFrame(form, fg_color="transparent")
            current_row.pack(fill="x", pady=row_pady, padx=5)

        field_name = field['name']
        field_type = field.get('type', 'text')
        field_subtype = field.get('subtype', 'text')
        field_default = field.get('default', '')
        field_required = field.get('required', False)
        small_field = field.get('small', False)
        
        # Field container
        field_frame = ctk.CTkFrame(current_row, fg_color="transparent")
        field_frame.pack(fill="x" if not small_field else None, padx=5, side="left", expand=not small_field)
        
        # Create appropriate input widget
        if field_type == 'text':
            entry_kwargs = {
                "placeholder_text": field.get("placeholder", field_name),
                "height": input_height,
                "font": ("Arial", input_font_size),
                "corner_radius": ROUND_INPUT,
            }
            widget = ctk.CTkEntry(field_frame, **entry_kwargs)

            if field_subtype == 'password':
                widget.configure(show="•")
            elif field_subtype == 'number':
                vcmd = (widget.register(input_validation.validate_number_input), '%P')
                widget.configure(validate="key", validatecommand=vcmd)

            elif field_subtype == 'currency':
                # Currency validation: allows numbers with optional decimal and max 2 decimal places
                vcmd = (widget.register(input_validation.validate_currency_input), '%P')
                widget.configure(validate="key", validatecommand=vcmd)

            elif field_subtype == 'date':
                # Date validation: allows YYYY-MM-DD format with required hyphens.
                # Add calendar picker trigger next to date fields.
                date_row = ctk.CTkFrame(field_frame, fg_color="transparent")
                date_row.pack(fill="x", expand=True)

                # Recreate inside date_row instead of re-packing into a different parent.
                # This avoids layout collapse where only the calendar icon appears.
                widget.destroy()
                entry_kwargs["width"] = 140
                widget = ctk.CTkEntry(date_row, **entry_kwargs)
                vcmd = (widget.register(input_validation.validate_date_input), '%P')
                widget.configure(validate="key", validatecommand=vcmd)
                widget.pack(side="left", fill="x", expand=True)

                # Use centralized date picker from ui_utilities
                # Capture widget by value using default argument to avoid closure issue
                def open_calendar(target_widget=widget):
                    ui_utils.open_date_picker(target_widget, parent.winfo_toplevel())

                ctk.CTkButton(
                    date_row,
                    text="📅",
                    width=34,
                    height=input_height,
                    font=("Arial", 13),
                    command=open_calendar,
                    fg_color=("gray80", "gray25"),
                    hover_color=("gray70", "gray30"),
                ).pack(side="left", padx=(6, 0))

            if field_default:
                widget.insert(0, str(field_default))
            if field_subtype != 'date':
                widget.pack(fill="x")
            
        elif field_type == 'dropdown':
            options = field.get('options', [])
            
            widget = ctk.CTkOptionMenu(
                field_frame,
                values=options,
                height=input_height,
                font=("Arial", input_font_size)
            )
            
            if field_default and field_default in options:
                widget.set(field_default)
            elif options:
                widget.set(options[0])
            widget.pack(fill="x")
            
        elif field_type == 'checkbox':
            widget = ctk.CTkCheckBox(
                field_frame,
                text="",
                font=("Arial", input_font_size)
            )
            if field_default:
                widget.select()
            widget.pack(anchor="w")
        
        field_widgets[field_name] = {'widget': widget, 'type': field_type, 'required': field_required}
        fields_count += 1
    
    # Error message label (initially hidden)
    error_label = ctk.CTkLabel(
        form,
        text="",
        font=("Arial", 12),
        text_color="red",
        wraplength=400
    )
    
    # Success message label (initially hidden)
    success_label = ctk.CTkLabel(
        form,
        text="",
        font=("Arial", 12),
        text_color="green",
        wraplength=400
    )
    
    # Submit button
    def handle_submit():
        # Clear previous messages
        error_label.pack_forget()
        success_label.pack_forget()
        
        # Collect values from all fields
        values = {}
        all_valid = True
        
        for field_name, field_info in field_widgets.items():
            widget = field_info['widget']
            field_type = field_info['type']
            required = field_info['required']
            
            # Get value based on widget type
            if field_type == 'text':
                value = widget.get().strip()
            elif field_type == 'dropdown':
                value = widget.get()
            elif field_type == 'checkbox':
                value = widget.get() == 1
            else:
                value = None
            
            # Validate required fields
            if required and (value == '' or value is None):
                all_valid = False
                error_label.configure(text=f"Error: {field_name} is required")
                error_label.pack(pady=0, padx=10)
                break
            
            values[field_name] = value
        
        # Call the callback if validation passes
        if all_valid and on_submit:
            result = on_submit(values)
            # If callback returns a string, it's an error message
            if isinstance(result, str):
                error_label.configure(text=result)
                error_label.pack(pady=0, padx=10)
            elif result is True:
                # Success - show success message
                success_label.configure(text="Operation completed successfully.")
                success_label.pack(pady=0, padx=10)
                # Clear all input fields after successful submission
                for field_name, field_info in field_widgets.items():
                    widget = field_info['widget']
                    field_type = field_info['type']
                    
                    if field_type == 'text':
                        widget.delete(0, 'end')
                    elif field_type == 'checkbox':
                        widget.deselect()
                    elif field_type == 'dropdown':
                        # Find the original field definition to get options
                        field_def = next((f for f in fields if f['name'] == field_name), None)
                        if field_def:
                            options = field_def.get('options', [])
                            if options:
                                widget.set(options[0])
    
    submit_button = ctk.CTkButton(
        form,
        text=submit_text,
        command=handle_submit,
        height=button_height,
        font=("Arial", button_font_size, "bold"),
        corner_radius=ROUND_BTN,
        fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
        hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
        text_color=("white", "white"),
    )
    submit_button.pack(pady=(10, 5), padx=10, fill="x")
    
    return form, error_label