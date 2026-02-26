"""UI card components for displaying organized content.

This module provides card-style UI elements including:
- function_card: Main card container for role-based functions
- action_button: Standard action button with consistent sizing
- popup_card: Modal popup with overlay
- info_badge: Styled info badge with yellow/brown theme
- location_dropdown_with_label: Location selection dropdown
- stat_card: Metric display card
- stats_grid: Container for stat cards
"""

import customtkinter as ctk
from config.theme import PRIMARY_BLUE, PRIMARY_BLUE_HOVER, ROUND_BOX, ROUND_INPUT
import database_operations.repos.location_repository as location_repo


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
    from .ui_utilities import content_separator
    
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


def popup_card(parent, title, small=False, button_text="Open", button_size="medium", generate_button=True):
    """Create a popup card that appears as an overlay.
    
    This creates a modal popup that covers the entire window with a semi-transparent overlay.
    The popup includes a close button and a content area for custom widgets.
    
    Args:
        parent: The parent container
        title: Popup title text
        small: Use small centered popup (default: False for large popup)
        button_text: Text for the trigger button (default: "Open")
        button_size: Size of the trigger button (default: "medium")
        generate_button: Whether to create a trigger button (default: True)
        
    Returns:
        Tuple of (button, open_popup_function):
        - button: The trigger button widget (or None if generate_button=False)
        - open_popup_function: Function to open the popup programmatically
        
    Example:
        btn, open_fn = popup_card(parent, "Edit User")
        content = btn  # The content area is returned by open_fn when called
        # Add widgets to content...
    """
    from .ui_utilities import content_separator
    
    # Store reference to overlay for closing
    overlay_ref = {'overlay': None, 'popup': None}
    
    def close_popup():
        """Close and destroy the popup overlay"""
        if overlay_ref['overlay']:
            overlay_ref['overlay'].destroy()
            overlay_ref['overlay'] = None
            overlay_ref['popup'] = None
    
    def open_popup():
        """Open the popup and return the content container"""
        # Close existing popup if open
        close_popup()
        
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


def info_badge(parent, text: str, side="left", padx=6):
    """Create a styled info badge with yellow/brown theme.
    
    Args:
        parent: The parent container
        text: Badge text content
        side: Pack side (default: "left")
        padx: Horizontal padding (default: 6)
        
    Returns:
        The badge label widget (can be updated with .configure(text="..."))
    """
    badge = ctk.CTkLabel(
        parent,
        text=text,
        font=("Arial", 12, "bold"),
        text_color=("#6E4B00", "#F5D27A"),
        fg_color=("#F4D28A", "#4B360D"),
        corner_radius=ROUND_INPUT,
        padx=10,
        pady=6,
    )
    badge.pack(side=side, padx=padx)
    return badge


def location_dropdown_with_label(parent, initial_value="All Locations", side="left", padx=(12, 0)):
    """Create a location dropdown with a label.
    
    This creates a "Location" label followed by a dropdown containing all cities
    from the location repository, plus "All Locations" option.
    
    Args:
        parent: The parent container
        initial_value: Initial dropdown value (default: "All Locations")
        side: Pack side for the wrapper (default: "left")
        padx: Horizontal padding for the wrapper (default: (12, 0))
        
    Returns:
        The dropdown widget (CTkComboBox)
    """
    location_wrap = ctk.CTkFrame(parent, fg_color="transparent")
    location_wrap.pack(side=side, padx=padx)

    ctk.CTkLabel(
        location_wrap,
        text="Location",
        font=("Arial", 13, "bold"),
        text_color=("gray35", "gray75"),
    ).pack(side="left", padx=(0, 10))

    try:
        cities = ["All Locations"] + location_repo.get_all_cities()
    except Exception as e:
        print(f"Error loading cities: {e}")
        cities = ["All Locations"]

    location_dropdown = ctk.CTkComboBox(location_wrap, values=cities, width=240, font=("Arial", 13))
    location_dropdown.set(initial_value)
    location_dropdown.pack(side="left")
    
    return location_dropdown


def stat_card(parent, title: str, default_value: str = "0"):
    """Create a stat card displaying a metric with title and value.
    
    This creates a rounded card with a title at the top and a large value below it.
    Common for displaying dashboard metrics like revenue, counts, etc.
    
    Args:
        parent: The parent container (should be a stats grid frame)
        title: The metric title (will be converted to uppercase)
        default_value: Initial value to display (default: "0")
        
    Returns:
        The value label widget (update with .configure(text="..."))
    """
    card = ctk.CTkFrame(
        parent,
        corner_radius=ROUND_BOX,
        fg_color=("gray92", "gray17"),
        border_width=1,
        border_color=("gray80", "gray28"),
    )
    card.pack(side="left", expand=True, fill="both", padx=6, ipadx=8, ipady=10)

    ctk.CTkLabel(
        card,
        text=title.upper(),
        font=("Arial", 11, "bold"),
        text_color=("gray45", "gray70"),
        anchor="w",
    ).pack(fill="x", padx=12, pady=(8, 0))

    value = ctk.CTkLabel(
        card,
        text=default_value,
        font=("Arial", 20, "bold"),
        text_color=("#3B8ED0", "#3B8ED0"),
        anchor="w",
    )
    value.pack(fill="x", padx=12, pady=(2, 8))
    return value


def stats_grid(parent, pady=(0, 4)):
    """Create a container for holding stat cards in a horizontal grid.
    
    Args:
        parent: The parent container
        pady: Vertical padding (default: (0, 4))
        
    Returns:
        The stats container frame (add stat_card widgets to this)
    """
    stats = ctk.CTkFrame(parent, fg_color="transparent")
    stats.pack(fill="x", pady=pady)
    return stats
