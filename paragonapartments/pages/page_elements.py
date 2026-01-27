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


def action_button(parent, text, command, size="medium", pady=8, padx=5, side=None):
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