import customtkinter as ctk
import re
from PIL import Image

# Import page elements for use in user dashboard and other pages

def content_container(parent, anchor=None, side=None,
                     margin=10, marginx=None, marginy=None,
                     padding=15, paddingx=None, paddingy=None,
                     hasBG=True, expand=False, fill=None):
    """Create and return a container frame for page content.
    
    Args:
        parent: The parent widget
        anchor: Anchor position (n, s, e, w, ne, nw, se, sw, center)
        side: Pack side (top, bottom, left, right)
        margin: External spacing (default for marginx/marginy)
        marginx: Horizontal external spacing
        marginy: Vertical external spacing
        padding: Internal spacing (default for paddingx/paddingy)
        paddingx: Horizontal internal spacing
        paddingy: Vertical internal spacing
        hasBG: Whether to show background color
        expand: Whether container expands to fill space
        fill: Fill direction (x, y, both, none)
    """
    if marginy is None: marginy = margin
    if marginx is None: marginx = margin
    if paddingy is None: paddingy = padding
    if paddingx is None: paddingx = padding

    container = ctk.CTkFrame(parent, fg_color="transparent" if not hasBG else None)
    container.pack(expand=expand, fill=fill, anchor=anchor, side=side, 
                   padx=marginx, pady=marginy, ipadx=paddingx, ipady=paddingy)
    return container


def round_image_corners(image, radius):
    """Add rounded corners to an image."""
    from PIL import ImageDraw
    
    # Create a mask with rounded corners
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    
    # Apply the mask
    output = Image.new('RGBA', image.size)
    output.paste(image, (0, 0))
    output.putalpha(mask)
    
    return output
    

def content_separator(parent, pady=(5, 10), padx=15):
    """Add a visual separator line.
    
    Args:
        parent: The parent container
        pady: Vertical padding (top, bottom)
        padx: Horizontal padding
        color: Separator line color
    """
    separator = ctk.CTkFrame(parent, height=2, fg_color="gray35")
    separator.pack(fill="x", pady=pady, padx=padx)
    return separator

def vertical_divider(parent, pady=5, padx=(0, 5)):
    """Add a visual separator line.
    
    Args:
        parent: The parent container
        pady: Vertical padding (top, bottom)
        padx: Horizontal padding
        color: Separator line color
    """
    separator = ctk.CTkFrame(parent, width=2, height=1, fg_color="gray35")
    separator.pack(fill="y", side="left", padx=padx, pady=pady)
    return separator


def function_card(parent, title, side="left", anchor="nw", pady=10, padx=10):
    """Create a card container for user functions with a title.
    
    This creates a bordered card that can hold function-specific content.
    Multiple cards can be packed together to create role-based dashboards.
    Cards automatically resize to fit the width of the page.
    
    Args:
        parent: The parent container
        title: Title text displayed at the top of the card
        side: Pack side (left, right, top, bottom) - use "left" for multi-column layouts
        anchor: Anchor position
        pady: Vertical margin
        padx: Horizontal margin
        
    Returns:
        The card's content container (add widgets to this)
    """

    # Outer card frame with border effect
    card = ctk.CTkFrame(parent, corner_radius=10)
    card.pack(side=side, pady=pady, padx=padx, anchor=anchor, expand=True, fill="both")
    
    ctk.CTkLabel(
        card,
        text=title,
        font=("Arial", 18, "bold"),
        anchor="w"
    ).pack(padx=15, pady=(10, 5))

    content_separator(card, pady=(0, 5))
    
    # Content area - this is what gets returned
    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=15, pady=(5, 15))
    
    return content


def action_button(parent, text, command, size="medium", pady=5, padx=5, side=None):
    """Create a standard action button with consistent sizing.
    
    Args:
        parent: The parent container
        text: Button text
        command: Button click callback
        size: Button size - "small" (180px), "medium" (250px), "large" (350px), "full" (fill width)
        pady: Vertical padding
        padx: Horizontal padding
        side: Pack side (left, right, top, bottom)
        
    Returns:
        The button widget
    """
    # Size mapping (width, height, font_size)
    sizes = {
        "small": (180, 36, 14),
        "medium": (250, 40, 16),
        "large": (350, 45, 18),
        "full": (0, 45, 16)
    }
    
    width, height, font_size = sizes.get(size, sizes["medium"])
    
    button = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        width=width,
        height=height,
        font=("Arial", font_size),
        corner_radius=8
    )
    
    if size == "full":
        button.pack(pady=pady, padx=padx, side=side, fill="x")
    else:
        button.pack(pady=pady, padx=padx, side=side)
    
    return button


def scrollable_container(parent, expand=True, fill="both", pady=10, padx=10):
    """Create a scrollable container for content that may exceed visible area.
    
    Args:
        parent: The parent container
        expand: Whether container expands to fill space
        fill: Fill direction (x, y, both, none)
        pady: Vertical padding
        padx: Horizontal padding
        
    Returns:
        The scrollable container (add widgets to this)
    """
    scrollable = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    scrollable.pack(expand=expand, fill=fill, pady=pady, padx=padx)
    return scrollable


def row_container(parent, pady=0):
    """Create a new content row container.
    
    Args:
        parent: The parent container
        pady: Vertical padding
        
    Returns:
        The row container
    """
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=pady, padx=10)
    return row


def form_element(parent, fields, name, submit_text="Submit", on_submit=None, pady=5, field_per_row=2, small=False):
    """Create a form with customizable fields and a submit button.
    
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
        submit_text: Text for the submit button
        on_submit: Callback function that receives dict of {field_name: value} and error_label.
                   Callback should return True for success, or error message string for failure.
        pady: Vertical padding between fields
        field_per_row: Number of fields per row (default: 2)
        small: Use smaller sizing for compact forms (default: False)
    Returns:
        Tuple of (form_container, error_label) - use error_label to show custom errors
        
    Example:
        def handle_submit(values, error_label):
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
    input_height = 28 if small else 35
    input_font_size = 11 if small else 13
    button_height = 32 if small else 40
    button_font_size = 13 if small else 16
    row_pady = 3 if small else 5
    
    form = ctk.CTkFrame(parent, fg_color="transparent")
    form.pack(fill="both", expand=True, pady=pady)

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
            widget = ctk.CTkEntry(
                field_frame,
                placeholder_text=field_name,
                height=input_height,
                font=("Arial", input_font_size)
            )

            if field_subtype == 'password':
                widget.configure(show="•")
            elif field_subtype == 'number':
                # # NOTE: Using Tk validate/validatecommand can break CustomTkinter placeholders
                # # on some platforms/themes. We sanitize on key release instead.
                # def sanitize_number(_event=None):
                #     current = widget.get()
                #     cleaned = "".join(ch for ch in current if ch.isdigit())
                #     if cleaned != current:
                #         widget.delete(0, "end")
                #         widget.insert(0, cleaned)
                # widget.bind("<KeyRelease>", sanitize_number)

######## Old code reverted because of issues ####################
                def only_numbers(proposed_value):
                    return proposed_value.isdigit() or proposed_value == ""
                vcmd = (widget.register(only_numbers), '%P')
                widget.configure(validate="key", validatecommand=vcmd)
######## Old code reverted because of issues ####################

            elif field_subtype == 'currency':
                # # NOTE: Using Tk validate/validatecommand can break CustomTkinter placeholders
                # # on some platforms/themes. We sanitize on key release instead.
                # def sanitize_currency(_event=None):
                #     current = widget.get()
                #     # Keep digits and at most one dot
                #     cleaned_chars = []
                #     dot_seen = False
                #     for ch in current:
                #         if ch.isdigit():
                #             cleaned_chars.append(ch)
                #         elif ch == "." and not dot_seen:
                #             cleaned_chars.append(ch)
                #             dot_seen = True
                #     cleaned = "".join(cleaned_chars)
                #     # Enforce max 2 decimals
                #     if "." in cleaned:
                #         left, right = cleaned.split(".", 1)
                #         cleaned = left + "." + right[:2]
                #     if cleaned != current:
                #         widget.delete(0, "end")
                #         widget.insert(0, cleaned)
                # widget.bind("<KeyRelease>", sanitize_currency)

######## Old code reverted because of issues ####################
                # Currency validation: allows numbers with optional decimal and max 2 decimal places
                # Pattern: digits (optional: decimal point + max 2 digits)
                def validate_currency(proposed_value):
                    # Matches: empty, digits, or digits with .XX format (max 2 decimal places)
                    return re.match(r'^\d*\.?\d{0,2}$', proposed_value) is not None
                
                vcmd = (widget.register(validate_currency), '%P')
                widget.configure(validate="key", validatecommand=vcmd)
######## Old code reverted because of issues ####################

            elif field_subtype == 'date':
                # Date validation: allows DD-MM-YYYY format with required hyphens
                def validate_date(proposed_value):
                    # Matches: empty or DD-MM-YYYY format (progressive: "", "0", "01", "01-", "01-0", "01-02", "01-02-", "01-02-2026")
                    # Enforces hyphens in correct positions
                    return re.match(r'^(\d{0,2}(-\d{0,2}(-\d{0,4})?)?)?$', proposed_value) is not None
                
                vcmd = (widget.register(validate_date), '%P')
                widget.configure(validate="key", validatecommand=vcmd)

            if field_default:
                widget.insert(0, str(field_default))
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
        corner_radius=8
    )
    submit_button.pack(pady=(10, 5), padx=10, fill="x")
    
    return form, error_label


def popup_card(parent, title, button_text="", small=False, button_size="medium", generate_button=True):
    """Create a popup card that opens when a button is clicked.
    
    This creates a button that, when clicked, displays a modal popup with a darkened
    background overlay. The popup can contain forms, inputs, or any other content.
    
    Args:
        parent: The parent container
        button_text: Text displayed on the trigger button
        title: Title displayed at the top of the popup card
        small: Boolean indicating if the popup is small (True) or fullscreen (False)
        button_size: Size of the trigger button - "small", "medium", "large", "full"
        
    Returns:
        Tuple of (button_widget, content_container):
        - button_widget: The button that opens the popup (or None if generate_button is False)
        - content_container: The container inside the popup where you add your content
        
    Example:
        button, content = popup_card(parent, "Create User", "New User Form", small=True)
        # Add form or other widgets to 'content'
        fields = [{'name': 'Username', 'type': 'text'}]
        form, error = form_element(content, fields, name=None, submit_text="Submit")
    """
    # Store overlay and popup references
    overlay_ref = {'overlay': None, 'popup': None}
    
    def close_popup():
        """Close and destroy the popup and overlay"""
        if overlay_ref['overlay']:
            overlay_ref['overlay'].destroy()
            overlay_ref['overlay'] = None
            overlay_ref['popup'] = None
    
    def open_popup():
        """Create and display the popup with darkened overlay"""
        # Get the top-level window to place overlay over entire window
        top_level = parent.winfo_toplevel()
        
        # Create semi-transparent overlay that slightly dims content but keeps it visible
        # Using lighter colors creates a subtle dimming effect
        overlay = ctk.CTkFrame(top_level, fg_color="transparent")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.lift()
        
        # Close popup when clicking overlay background
        overlay.bind("<Button-1>", lambda e: close_popup())
        
        # Create popup card
        if not small:
            popup = ctk.CTkFrame(overlay, corner_radius=10)
            popup.place(relx=0.015, rely=0.015, relwidth=0.97, relheight=0.97)
        else:  # small
            popup = ctk.CTkFrame(overlay, corner_radius=10)
            popup.place(relx=0.5, rely=0.5, anchor="center")
        
        # Store references
        overlay_ref['overlay'] = overlay
        overlay_ref['popup'] = popup
        
        # Prevent popup clicks from closing the overlay
        popup.bind("<Button-1>", lambda e: "break")
        
        # Header with title and close button
        header = ctk.CTkFrame(popup, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            header,
            text=title,
            font=("Arial", 18, "bold"),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
        
        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=30,
            height=30,
            font=("Arial", 18),
            command=close_popup,
            fg_color=("gray70", "gray25"),
            hover_color=("gray60", "gray20")
        )
        close_btn.pack(side="right")
        
        content_separator(popup, pady=(0, 5))
        
        # Content area - this is what gets returned
        content = ctk.CTkFrame(popup, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        return content
    
    # Create trigger button
    if generate_button:
        button = action_button(parent, button_text, open_popup, size=button_size)
    else:
        button = None
    
    return button, open_popup


def data_table(parent, columns, data=None, editable=False, deletable=False,
               on_update=None, on_delete=None, refresh_data=None,
               show_refresh_button: bool = True,
               render_batch_size: int = 0,
               page_size: int = 0,
               **_kwargs):
    """Create a data table with optional CRUD operations.
    
    This creates a scrollable table that displays data with optional edit and delete
    functionality for each row. If create callback is provided, an "Add Row" button appears.
    
    Args:
        parent: The parent container
        columns: List of column dictionaries with keys:
            - 'name': Column header name (required)
            - 'key': Data key for this column (required)
            - 'width': Column width in pixels (default: 150)
            - 'editable': Whether this column is editable (default: True if table editable)
        data: List of dictionaries representing rows (optional, can be loaded later)
        editable: Enable edit functionality for rows
        deletable: Enable delete functionality for rows
        on_update: Callback function(row_data, updated_data) for updating a row
        on_delete: Callback function(row_data) for deleting a row
        refresh_data: Callback function() that returns updated data list
        
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
            {'name': 'Username', 'key': 'username', 'width': 200},
            {'name': 'Email', 'key': 'email', 'width': 250}
        ]
        
        table, refresh = data_table(parent, columns, editable=True, deletable=True,
                                   on_update=update_row, on_delete=delete_row,
                                   refresh_data=get_data)
    """
    # Main table container
    table_container = ctk.CTkFrame(parent)
    table_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Store reference to content area for refreshing
    content_ref = {'content': None}
    pagination_ref = {"page": 1, "total_pages": 1}
    
    def refresh_table():
        """Refresh the table data"""
        # Get fresh data if refresh callback provided
        current_data = refresh_data() if refresh_data else data or []
        total_rows = len(current_data)
        
        # Create scrollable content area on first call, or clear existing children
        if content_ref['content'] is None:
            content = scrollable_container(table_container, pady=0, padx=0)
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
            vertical_divider(header_row, padx=(0, 8))
        
        # Actions column header if editable or deletable
        if editable or deletable:
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
                refresh_btn.pack(padx=25, side="left"if (ps > 0 and total_rows > ps) else None) # Align left if pagination exists, otherwise right

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
                                 on_update, on_delete, refresh_table)
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
                         update_callback, delete_callback, refresh_callback):
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
                try:
                    if raw_value == "" or raw_value is None:
                        value = ""
                    else:
                        value = f"£{float(raw_value):,.2f}"
                except Exception:
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
                                            update_callback, refresh_callback),
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
                    command=lambda: delete_row(row_data, delete_callback, refresh_callback),
                    fg_color=("red", "darkred"),
                    hover_color=("darkred", "red")
                )
                delete_btn.pack(side="left", padx=2)
    
    def edit_row(row_data, cell_widgets, cols, update_callback, refresh_callback):
        """Enable editing for a row"""
        edit_data = {}
        
        # Convert labels to entries
        for col in cols:
            col_key = col['key']
            if col_key in cell_widgets and cell_widgets[col_key]['editable']:
                widget_info = cell_widgets[col_key]
                label = widget_info['label']
                current_value = label.cget("text")

                # If the column is formatted as currency, strip formatting for editing
                if col.get("format") == "currency" and isinstance(current_value, str):
                    current_value = current_value.replace("£", "").replace(",", "").strip()
                
                # Replace label with entry
                label.pack_forget()
                entry = ctk.CTkEntry(
                    label.master,
                    width=col.get('width', 150),
                    font=("Arial", 12)
                )
                entry.insert(0, current_value)
                entry.pack()
                edit_data[col_key] = entry
        
        # Change edit button to save
        if cell_widgets:
            first_cell = list(cell_widgets.values())[0]
            button_frame = first_cell['label'].master.master
            
            # Find and update buttons
            for widget in button_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for btn in widget.winfo_children():
                        if isinstance(btn, ctk.CTkButton) and btn.cget("text") == "Edit":
                            btn.configure(
                                text="Save",
                                command=lambda: save_row(row_data, edit_data, 
                                                        update_callback, refresh_callback)
                            )
    
    def save_row(row_data, edit_data, update_callback, refresh_callback):
        """Save edited row data"""
        updated_data = {key: entry.get() for key, entry in edit_data.items()}
        
        if update_callback:
            result = update_callback(row_data, updated_data)
            if result is True:
                refresh_callback()
            else:
                # Show error (could be enhanced with error display)
                print(f"Update failed: {result}")
    
    def delete_row(row_data, delete_callback, refresh_callback):
        """Delete a row"""
        if delete_callback:
            result = delete_callback(row_data)
            if result is True:
                refresh_callback()
            else:
                print(f"Delete failed: {result}")
    
    # Initial table load
    refresh_table()
    
    return table_container, refresh_table