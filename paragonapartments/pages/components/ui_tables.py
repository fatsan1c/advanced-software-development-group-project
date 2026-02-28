"""Data table UI components for displaying and managing tabular data.

This module provides comprehensive data table functionality including:
- data_table: Full-featured table with CRUD operations
- Pagination support for large datasets
- Batch rendering for responsive UI
- Inline editing and deletion
- Custom column formatting (text, number, currency, date, dropdown)
- Scrollable container support
"""

import customtkinter as ctk
import pages.components.input_validation as input_validation


def data_table(parent, columns, data=None, editable=False, deletable=False,
               on_update=None, on_delete=None, refresh_data=None,
               show_refresh_button: bool = True,
               render_batch_size: int = 0,
               page_size: int = 0, scrollable: bool = False,
               **_kwargs):
    """Create a data table with optional CRUD operations.
    
    This creates table that displays data with optional edit and delete
    functionality for each row. If create callback is provided, an "Add Row" button appears.
    
    Args:
        parent: The parent container
        columns: List of column dictionaries with keys:
            - 'name': Column header name (required)
            - 'key': Data key for this column (required)
            - 'width': Column width in pixels (default: 150)
            - 'editable': Whether this column is editable (default: True if table editable)
            - 'format': Optional format with validation - "text", "number", "currency", "date", "dropdown", "boolean"
            - 'options': List of options for dropdown format, OR [true_label, false_label] for boolean format
                        Boolean example: ['Active', 'Inactive'] automatically maps 1→Active, 0→Inactive
        data: List of dictionaries representing rows (optional, can be loaded later)
        editable: Enable edit functionality for rows
        deletable: Enable delete functionality for rows
        on_update: Callback function(row_data, updated_data) for updating a row
        on_delete: Callback function(row_data) for deleting a row
        refresh_data: Callback function() that returns updated data list
        show_refresh_button: Whether to show a refresh button for manual data refresh
        render_batch_size: If > 0, renders rows in batches of this size to keep UI responsive
        page_size: If > 0, enables pagination with this many rows per page
        scrollable: Whether to render the table inside a scrollable container (recommended for large tables)

    Returns:
        Tuple of (table_container, refresh_function):
        - table_container: The table widget
        - refresh_function: Function to refresh table data
        
    Example:
        def update_row(row, updated):
            user_repo.update_user(row['id'], updated)
            return True  # or error message string
            
        def delete_row(row):
            user_repo.delete_user(row['id'])
            return True
            
        def create_row(new_data):
            user_repo.create_user(new_data)
            return True
            
        def get_data():
            return user_repo.get_all_users()
        
        columns = [
            {'name': 'ID', 'key': 'id', 'width': 80, 'editable': False},
            {'name': 'Username', 'key': 'username', 'width': 200, 'format': 'text'},
            {'name': 'Status', 'key': 'status', 'width': 150, 'format': 'dropdown', 
             'options': ['Active', 'Inactive', 'Pending']},
            {'name': 'Active', 'key': 'is_active', 'width': 120, 'format': 'boolean',
             'options': ['Yes', 'No']},  # Display Yes/No, store as 1/0
            {'name': 'Balance', 'key': 'balance', 'width': 150, 'format': 'currency'},
            {'name': 'Age', 'key': 'age', 'width': 100, 'format': 'number'}
        ]
        
        table, refresh = data_table(parent, columns, editable=True, deletable=True,
                                   on_update=update_row, on_delete=delete_row,
                                   refresh_data=get_data)
    """
    from .ui_containers import scrollable_container
    from .ui_utilities import vertical_divider
    
    # Main table container
    table_container = ctk.CTkFrame(parent)
    table_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Error label (initially hidden)
    error_label = ctk.CTkLabel(
        table_container,
        text="",
        font=("Arial", 12),
        text_color="red",
        wraplength=600
    )
    
    # Store reference to content area for refreshing
    content_ref = {'content': None}
    pagination_ref = {"page": 1, "total_pages": 1}
    
    def refresh_table():
        """Refresh the table data"""
        # Hide error label on refresh
        error_label.pack_forget()
        
        # Get fresh data if refresh callback provided
        current_data = refresh_data() if refresh_data else data or []
        total_rows = len(current_data)
        
        # Create scrollable content area on first call, or clear existing children
        if content_ref['content'] is None:
            if scrollable:
                content = scrollable_container(table_container, pady=0, padx=0)
            else:
                content = ctk.CTkFrame(table_container, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=0, pady=0)
            content_ref['content'] = content
        else:
            # Clear all children from existing container
            for widget in content_ref['content'].winfo_children():
                widget.destroy()
            content = content_ref['content']
        
        # Header row
        header_row = ctk.CTkFrame(content, fg_color=("gray75", "gray25"))
        header_row.pack(fill="x", padx=5, pady=(5, 0))
        
        for col in columns:
            col_width = col.get('width', 150)
            header_cell = ctk.CTkLabel(
                header_row,
                text=col['name'],
                width=col_width-10,
                font=("Arial", 13, "bold"),
                anchor="w"
            )
            header_cell.pack(side="left", padx=5, pady=8)
            if col != columns[-1]:  # Don't add divider after last column
                vertical_divider(header_row, padx=(0, 8))
        
        # Actions column header if editable or deletable
        if editable or deletable:
            vertical_divider(header_row, padx=(0, 8))
            ctk.CTkLabel(
                header_row,
                text="Actions",
                width=120,
                font=("Arial", 13, "bold"),
                anchor="center"
            ).pack(side="right", padx=5, pady=8)
        
        # Pagination math (in-memory pagination; keeps UI responsive and avoids rendering all rows)
        ps = int(page_size or 0)
        if ps > 0:
            total_pages = max(1, (total_rows + ps - 1) // ps)
            pagination_ref["total_pages"] = total_pages
            pagination_ref["page"] = max(1, min(int(pagination_ref["page"]), total_pages))
            start = (pagination_ref["page"] - 1) * ps
            end = start + ps
            page_data = current_data[start:end]
        else:
            pagination_ref["total_pages"] = 1
            pagination_ref["page"] = 1
            page_data = current_data

        # Data rows (optionally render in batches to keep UI responsive)
        batch_size = int(render_batch_size or 0)
        batch_size = batch_size if batch_size > 0 else 0

        # Loading indicator for large tables
        loading_label = None
        if batch_size and len(page_data) > batch_size:
            loading_label = ctk.CTkLabel(
                content,
                text=f"Loading {len(page_data)} rows...",
                font=("Arial", 12),
                text_color=("gray25", "gray70"),
            )
            loading_label.pack(anchor="w", padx=5, pady=(8, 2))

        def finalize_controls():
            """Add table-level controls after rows render."""
            if loading_label:
                loading_label.destroy()

            # Add container for pagination or refresh button (to avoid empty space when no pagination)
            if (ps > 0 and total_rows > ps) or show_refresh_button:
                pager = ctk.CTkFrame(content, fg_color="transparent")
                pager.pack(fill="x", pady=(10, 0), padx=5)

            # Pagination controls
            if ps > 0 and total_rows > ps:

                def set_page(p: int):
                    pagination_ref["page"] = p
                    refresh_table()

                prev_btn = ctk.CTkButton(
                    pager,
                    text="← Prev",
                    width=90,
                    height=32,
                    command=lambda: set_page(max(1, pagination_ref["page"] - 1)),
                    state="normal" if pagination_ref["page"] > 1 else "disabled",
                    fg_color=("gray70", "gray30"),
                    hover_color=("gray60", "gray25"),
                )
                prev_btn.pack(side="left")

                # Page buttons (compact window with first/last)
                page_btn_frame = ctk.CTkFrame(pager, fg_color="transparent")
                page_btn_frame.pack(side="left", padx=10)

                cur = pagination_ref["page"]
                total = pagination_ref["total_pages"]

                def add_page_button(label, page_num=None, disabled=False):
                    btn = ctk.CTkButton(
                        page_btn_frame,
                        text=str(label),
                        width=38,
                        height=32,
                        command=(lambda p=page_num: set_page(p)) if page_num else None,
                        state="disabled" if disabled else "normal",
                        fg_color=("gray70", "gray30"),
                        hover_color=("gray60", "gray25"),
                    )
                    btn.pack(side="left", padx=2)

                # Determine which page numbers to show
                window = 2
                pages = []
                pages.append(1)
                for p in range(max(2, cur - window), min(total, cur + window) + 1):
                    pages.append(p)
                if total not in pages:
                    pages.append(total)

                # Render with ellipses
                last = None
                for p in pages:
                    if last is not None and p - last > 1:
                        add_page_button("…", disabled=True)
                    add_page_button(p, page_num=p, disabled=(p == cur))
                    last = p

                next_btn = ctk.CTkButton(
                    pager,
                    text="Next →",
                    width=90,
                    height=32,
                    command=lambda: set_page(min(total, pagination_ref["page"] + 1)),
                    state="normal" if pagination_ref["page"] < total else "disabled",
                    fg_color=("gray70", "gray30"),
                    hover_color=("gray60", "gray25"),
                )
                next_btn.pack(side="left", padx=(10, 0))

                ctk.CTkLabel(
                    pager,
                    text=f"Page {cur} / {total} ({total_rows} rows)",
                    font=("Arial", 12),
                    text_color=("gray25", "gray70"),
                ).pack(side="right")

            # Refresh button
            if show_refresh_button:
                refresh_btn = ctk.CTkButton(
                    pager,
                    text="⟳ Refresh",
                    command=refresh_table,
                    height=32,
                    width=110,
                    fg_color=("gray70", "gray30"),
                    hover_color=("gray60", "gray25")
                )
                refresh_btn.pack(padx=25, side="left" if (ps > 0 and total_rows > ps) else None)  # Align left if pagination exists, otherwise right

        def render_rows_range(start_idx: int):
            end_idx = len(page_data) if not batch_size else min(start_idx + batch_size, len(page_data))
            for row_data in page_data[start_idx:end_idx]:
                create_row_widget(
                    content,
                    row_data,
                    columns,
                    editable,
                    deletable,
                    on_update,
                    on_delete,
                    refresh_table,
                    error_label,
                )

            if end_idx < len(page_data):
                # Schedule next batch; keeps UI responsive during heavy renders
                table_container.after(1, lambda: render_rows_range(end_idx))
            else:
                finalize_controls()

        if batch_size:
            render_rows_range(0)
        else:
            for row_data in page_data:
                create_row_widget(content, row_data, columns, editable, deletable,
                                 on_update, on_delete, refresh_table, error_label)
            finalize_controls()
    
    # Expose pagination controls to callers (backwards-compatible)
    def _set_page(p: int):
        pagination_ref["page"] = int(p)
        refresh_table()

    def _reset_page():
        pagination_ref["page"] = 1

    refresh_table.set_page = _set_page  # type: ignore[attr-defined]
    refresh_table.reset_page = _reset_page  # type: ignore[attr-defined]

    def create_row_widget(parent_widget, row_data, cols, is_editable, is_deletable, 
                         update_callback, delete_callback, refresh_callback, error_label):
        """Create a single row in the table"""
        row = ctk.CTkFrame(parent_widget, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=2)
        
        # Store widgets for editing
        cell_widgets = {}
        
        for col in cols:
            col_width = col.get('width', 150)
            col_key = col['key']
            col_editable = col.get('editable', True)
            raw_value = row_data.get(col_key, '')

            # Optional formatting helpers (backwards-compatible)
            value = raw_value
            col_format = col.get("format")
            if col_format == "currency":
                value = input_validation.format_currency_display(raw_value)
            elif col_format == "boolean":
                # Map 1/0 to display labels using options [true_label, false_label]
                options = col.get('options', ['True', 'False'])
                try:
                    value = options[0] if int(raw_value) == 1 else options[1]
                except (ValueError, TypeError, IndexError):
                    value = str(raw_value)
            else:
                # Default: apply prefix/suffix if specified
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
                font=("Arial", 12)
            )
            cell_label.pack()
            
            cell_widgets[col_key] = {'label': cell_label, 'editable': col_editable}
        
        # Action buttons
        if is_editable or is_deletable:
            action_frame = ctk.CTkFrame(row, fg_color="transparent")
            action_frame.pack(side="right", padx=5)
            
            if is_editable:
                edit_btn = ctk.CTkButton(
                    action_frame,
                    text="Edit",
                    width=50,
                    height=28,
                    command=lambda: edit_row(row_data, cell_widgets, cols, 
                                            update_callback, refresh_callback, error_label),
                    fg_color=("gray70", "gray30"),
                    hover_color=("gray60", "gray25")
                )
                edit_btn.pack(side="left", padx=2)
            
            if is_deletable:
                delete_btn = ctk.CTkButton(
                    action_frame,
                    text="Delete",
                    width=60,
                    height=28,
                    command=lambda: delete_row(row_data, delete_callback, refresh_callback, error_label),
                    fg_color=("red", "darkred"),
                    hover_color=("darkred", "red")
                )
                delete_btn.pack(side="left", padx=2)
    
    def edit_row(row_data, cell_widgets, cols, update_callback, refresh_callback, error_label):
        """Enable editing for a row"""
        # Hide error label when starting edit
        error_label.pack_forget()
        edit_data = {}
        
        # Convert labels to entries
        for col in cols:
            col_key = col['key']
            if col_key in cell_widgets and cell_widgets[col_key]['editable']:
                widget_info = cell_widgets[col_key]
                label = widget_info['label']
                current_value = label.cget("text")
                col_format = col.get("format")

                # Strip formatting based on format type
                if col_format == "currency" and isinstance(current_value, str):
                    current_value = input_validation.strip_currency_formatting(current_value)
                # For other formats, current_value is already in the correct format for editing
                
                # Replace label with appropriate widget based on format type
                label.pack_forget()
                
                if col_format == "dropdown":
                    # Create dropdown widget
                    options = col.get('options', [])
                    dropdown = ctk.CTkOptionMenu(
                        label.master,
                        values=options if options else ["No options"],
                        width=col.get('width', 150),
                        height=28,
                        font=("Arial", 12)
                    )
                    
                    # Set current value if it exists in options
                    if current_value and options and current_value in options:
                        dropdown.set(current_value)
                    elif options:
                        dropdown.set(options[0])
                    
                    dropdown.pack()
                    edit_data[col_key] = dropdown

                elif col_format == "boolean":
                    # For boolean, use dropdown with customizable labels from options [true_label, false_label]
                    # Maps: options[0] → 1 (true), options[1] → 0 (false)
                    options = col.get('options', ['True', 'False'])
                    
                    dropdown = ctk.CTkOptionMenu(
                        label.master,
                        values=options,
                        width=col.get('width', 150),
                        height=28,
                        font=("Arial", 12)
                    )
                    # Current_value is already the display label (e.g., 'Active' or 'Inactive')
                    if current_value in options:
                        dropdown.set(current_value)
                    else:
                        dropdown.set(options[0])
                    dropdown.pack()
                    edit_data[col_key] = {'widget': dropdown, 'boolean_options': options}

                else:
                    # Create entry widget with validation
                    entry = ctk.CTkEntry(
                        label.master,
                        width=col.get('width', 150),
                        font=("Arial", 12)
                    )
                    
                    # Apply real-time validation based on format type
                    if col_format == "number":
                        vcmd = (entry.register(input_validation.validate_number_input), '%P')
                        entry.configure(validate="key", validatecommand=vcmd)
                    
                    elif col_format == "currency":
                        vcmd = (entry.register(input_validation.validate_currency_input), '%P')
                        entry.configure(validate="key", validatecommand=vcmd)
                    
                    elif col_format == "date":
                        vcmd = (entry.register(input_validation.validate_date_input), '%P')
                        entry.configure(validate="key", validatecommand=vcmd)
                        entry.configure(placeholder_text="YYYY-MM-DD")
                    
                    # For "text" format or no format, no special validation needed
                    
                    entry.insert(0, current_value)
                    entry.pack()
                    edit_data[col_key] = entry
        
        # Change edit button to save and delete button to cancel
        if cell_widgets:
            first_cell = list(cell_widgets.values())[0]
            button_frame = first_cell['label'].master.master
            
            # Find and update buttons
            for widget in button_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for btn in widget.winfo_children():
                        if isinstance(btn, ctk.CTkButton):
                            if btn.cget("text") == "Edit":
                                btn.configure(
                                    text="Save",
                                    command=lambda: save_row(row_data, edit_data, 
                                                            update_callback, refresh_callback, error_label)
                                )
                            elif btn.cget("text") == "Delete":
                                btn.configure(
                                    text="Cancel",
                                    command=lambda: refresh_callback(),
                                    fg_color=("gray70", "gray30"),
                                    hover_color=("gray60", "gray25")
                                )
    
    def save_row(row_data, edit_data, update_callback, refresh_callback, error_label):
        """Save edited row data"""
        # Hide error label before attempting save
        error_label.pack_forget()
        # Handle both Entry and OptionMenu widgets, including value_map and boolean conversion
        updated_data = {}
        for key, item in edit_data.items():
            # Check if item is a dict with special handling
            if isinstance(item, dict) and 'widget' in item:
                widget = item['widget']
                selected_label = widget.get()
                
                # Boolean format: Convert label back to 1/0
                if 'boolean_options' in item:
                    boolean_options = item['boolean_options']
                    # First option (e.g., 'Active') → 1, second option (e.g., 'Inactive') → 0
                    updated_data[key] = 1 if selected_label == boolean_options[0] else 0
                # Dropdown with value_map: Convert label to database value
                elif 'value_map' in item:
                    value_map = item['value_map']
                    updated_data[key] = value_map.get(selected_label, selected_label)
                else:
                    updated_data[key] = selected_label
            elif isinstance(item, ctk.CTkOptionMenu):
                updated_data[key] = item.get()
            else:  # CTkEntry
                updated_data[key] = item.get()
        
        if update_callback:
            result = update_callback(row_data, updated_data)
            if result is True:
                refresh_callback()
            else:
                # Show error in label
                error_message = str(result) if result else "Update failed"
                error_label.configure(text=f"Update failed: {error_message}")
                error_label.pack(fill="x", padx=10, pady=(5, 0))
    
    def delete_row(row_data, delete_callback, refresh_callback, error_label):
        """Delete a row"""
        # Hide error label before attempting delete
        error_label.pack_forget()
        
        if delete_callback:
            result = delete_callback(row_data)
            if result is True:
                refresh_callback()
            else:
                # Show error in label
                error_message = str(result) if result else "Delete failed"
                error_label.configure(text=f"Delete failed: {error_message}")
                error_label.pack(fill="x", padx=10, pady=(5, 0))
    
    # Initial table load
    refresh_table()
    
    return table_container, refresh_table


def create_edit_popup_with_table(popup_content, columns, get_data_func, on_delete_func, 
                                 on_update_func, include_location_filter=False):
    """Create a standardized edit popup with header, optional location filter, and data table.
    
    This creates the common popup structure used across Manager, Administrator, 
    and Finance Manager for editing records with a data table.
    
    Args:
        popup_content: Parent container for the popup content
        columns: List of column dictionaries for the data table
        get_data_func: Function to fetch data (should handle location filtering if needed)
        on_delete_func: Callback for delete operations
        on_update_func: Callback for update operations
        include_location_filter: Whether to include location dropdown filter (default: False)
        
    Returns:
        dict with keys:
            - 'header': Header frame
            - 'location_dropdown': Location dropdown (if include_location_filter=True)
            - 'table': Table container
            - 'refresh_table': Function to refresh the table
    """
    # Header
    header = ctk.CTkFrame(popup_content, fg_color="transparent")
    header.pack(fill="x", padx=10, pady=(5, 10))
    
    # Optional location filter
    location_dropdown = None
    if include_location_filter:
        from .ui_utilities import create_popup_header_with_location
        header, location_dropdown = create_popup_header_with_location(popup_content)
    
    # Create data table
    table, refresh_table = data_table(
        popup_content,
        columns,
        editable=True,
        deletable=True,
        refresh_data=get_data_func,
        on_delete=on_delete_func,
        on_update=on_update_func,
        show_refresh_button=False,
        render_batch_size=20,
        page_size=10,
    )
    
    # Add refresh button to header
    from .ui_utilities import create_refresh_button
    create_refresh_button(header, refresh_table, padx=0)
    
    return {
        'header': header,
        'location_dropdown': location_dropdown,
        'table': table,
        'refresh_table': refresh_table
    }

