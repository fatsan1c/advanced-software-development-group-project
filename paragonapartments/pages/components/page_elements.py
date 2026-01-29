import customtkinter as ctk

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

    content_separator(card, pady=(0, 10))
    
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


def form_element(parent, fields, submit_text="Submit", on_submit=None, pady=5, field_per_row=2, small=False):
    """Create a form with customizable fields and a submit button.
    
    Args:
        parent: The parent container
        fields: List of field dictionaries with keys:
            - 'name': Field name/label (required)
            - 'type': Input type - 'text', 'dropdown', 'checkbox' (default: 'text')
            - 'options': List of options for dropdown (required if type='dropdown')
            - 'default': Default value
            - 'placeholder': Placeholder text for text fields
            - 'required': Whether field is required (default: False)
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
            {'name': 'Username', 'type': 'text', 'placeholder': 'Enter username', 'required': True},
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
        field_default = field.get('default', '')
        field_required = field.get('required', False)
        
        # Field container
        field_frame = ctk.CTkFrame(current_row, fg_color="transparent")
        field_frame.pack(fill="x", padx=5, side="left", expand=True)
        
        # Create appropriate input widget
        if field_type == 'text':
            widget = ctk.CTkEntry(
                field_frame,
                placeholder_text=field.get('placeholder', field_name),
                height=input_height,
                font=("Arial", input_font_size)
            )
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
    
    # Submit button
    def handle_submit():
        # Clear previous error
        error_label.pack_forget()
        
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
                error_label.pack(pady=0, padx=10, before=None)
                break
            
            values[field_name] = value
        
        # Call the callback if validation passes
        if all_valid and on_submit:
            result = on_submit(values, error_label)
            # If callback returns a string, it's an error message
            if isinstance(result, str):
                error_label.configure(text=result)
                error_label.pack(pady=0, padx=10)
            elif result is True:
                # Success - ensure error is hidden
                error_label.pack_forget()
    
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