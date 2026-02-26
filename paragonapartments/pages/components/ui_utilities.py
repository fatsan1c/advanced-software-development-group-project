"""
UI Utilities - Helper functions for dates, buttons, and common patterns.
"""

import customtkinter as ctk
from PIL import Image, ImageDraw
from datetime import datetime
from pages.components.config.theme import PRIMARY_BLUE, PRIMARY_BLUE_HOVER

try:
    from tkcalendar import Calendar  # type: ignore[reportMissingImports]
except Exception:
    Calendar = None


# ============================= Date Utility Functions =============================
def parse_date_string(date_str):
    """
    Parse a date string in YYYY-MM-DD format to a date object.
    
    Args:
        date_str: String in YYYY-MM-DD format
        
    Returns:
        date object or None if invalid/empty
    """
    s = (date_str or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def open_date_picker(entry_widget, parent_window):
    """
    Open a calendar date picker popup for an entry widget.
    
    Args:
        entry_widget: CTkEntry widget to update with selected date
        parent_window: Parent window for the popup (usually content.winfo_toplevel())
    """
    popup = ctk.CTkToplevel(parent_window)
    popup.title("Select Date")
    popup.geometry("360x430")
    popup.resizable(False, False)
    popup.transient(parent_window)
    popup.grab_set()

    # Parse current value or default to today
    selected = parse_date_string(entry_widget.get())
    selected = selected or datetime.now().date()

    # Determine theme
    mode = str(ctk.get_appearance_mode()).lower()
    is_dark = mode == "dark"

    # Create styled shell frame
    shell = ctk.CTkFrame(
        popup,
        corner_radius=12,
        fg_color=("#F3F4F6", "#1F232A"),
        border_width=1,
        border_color=("#D8DCE2", "#2C313A"),
    )
    shell.pack(fill="both", expand=True, padx=8, pady=8)

    # Header
    ctk.CTkLabel(
        shell,
        text="Pick a Date",
        font=("Arial", 24, "bold"),
        text_color=("#22252B", "#E9ECF2"),
    ).pack(anchor="w", padx=12, pady=(12, 4))

    ctk.CTkLabel(
        shell,
        text="Format: YYYY-MM-DD",
        font=("Arial", 12),
        text_color=("#5E6672", "#AAB2BE"),
    ).pack(anchor="w", padx=12, pady=(0, 8))

    # Calendar widget (if available)
    if Calendar is None:
        ctk.CTkLabel(
            shell,
            text="Calendar unavailable.\nInstall tkcalendar package.",
            justify="center",
            font=("Arial", 12),
        ).pack(pady=18)
        ctk.CTkButton(shell, text="Close", command=popup.destroy, width=120).pack(pady=(10, 0))
        return

    # Calendar configuration
    cal_kwargs = {
        "selectmode": "day",
        "date_pattern": "yyyy-mm-dd",
        "year": selected.year,
        "month": selected.month,
        "day": selected.day,
    }
    
    # Theme-specific styling
    if is_dark:
        cal_kwargs.update(
            {
                "font": ("Arial", 17),
                "headersfont": ("Arial", 15, "bold"),
                "background": "#2A2F36",
                "foreground": "#E9ECF2",
                "bordercolor": "#2A2F36",
                "headersbackground": "#222831",
                "headersforeground": "#E9ECF2",
                "normalbackground": "#2A2F36",
                "normalforeground": "#E9ECF2",
                "weekendbackground": "#2A2F36",
                "weekendforeground": "#E9ECF2",
                "othermonthbackground": "#2A2F36",
                "othermonthforeground": "#7F8A98",
                "selectbackground": PRIMARY_BLUE,
                "selectforeground": "#FFFFFF",
            }
        )
    else:
        cal_kwargs.update(
            {
                "font": ("Arial", 17),
                "headersfont": ("Arial", 15, "bold"),
                "background": "#FFFFFF",
                "foreground": "#1B2430",
                "bordercolor": "#D7DBE2",
                "headersbackground": "#EEF2F7",
                "headersforeground": "#1B2430",
                "normalbackground": "#FFFFFF",
                "normalforeground": "#1B2430",
                "selectbackground": PRIMARY_BLUE,
                "selectforeground": "#FFFFFF",
            }
        )

    cal = Calendar(
        shell,
        **cal_kwargs,
        showweeknumbers=False,
    )
    cal.pack(fill="both", expand=True, padx=12, pady=(4, 10))

    # Apply selected date to entry
    def apply_date():
        entry_widget.delete(0, "end")
        entry_widget.insert(0, cal.get_date())
        popup.destroy()

    # Button row
    btn_row = ctk.CTkFrame(shell, fg_color="transparent")
    btn_row.pack(fill="x", padx=10, pady=(0, 10))
    
    ctk.CTkButton(
        btn_row,
        text="Cancel",
        command=popup.destroy,
        width=104,
        height=34,
        font=("Arial", 14),
        fg_color=("gray80", "gray28"),
        hover_color=("gray70", "gray33"),
    ).pack(side="left")
    
    ctk.CTkButton(
        btn_row,
        text="Use Date",
        command=apply_date,
        width=104,
        height=34,
        font=("Arial", 14),
        fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
        hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
    ).pack(side="right")


# ============================= Button Styling Utilities =============================
def style_primary_button(button, font_size=14):
    """
    Apply primary button styling (for main CTAs like "View Graphs").
    
    Args:
        button: CTkButton widget to style
        font_size: Font size for button text (default: 14)
    """
    try:
        from pages.components.config.theme import ROUND_BTN
        button.configure(
            height=40,
            font=("Arial", font_size, "bold"),
            corner_radius=ROUND_BTN,
            fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
            hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
        )
        button.pack_configure(fill="x", padx=6, pady=(2, 0))
    except Exception:
        pass


def style_secondary_button(button, font_size=13):
    """
    Apply secondary button styling (for edit/management actions).
    
    Args:
        button: CTkButton widget to style
        font_size: Font size for button text (default: 13)
    """
    try:
        from pages.components.config.theme import ROUND_BTN
        button.configure(
            height=40,
            font=("Arial", font_size, "bold"),
            corner_radius=ROUND_BTN,
            fg_color=("gray85", "gray25"),
            hover_color=("gray80", "gray30"),
            text_color=("gray15", "gray92"),
        )
        button.pack_configure(pady=(4, 0))
    except Exception:
        pass


# ============================= Common UI Patterns =============================
def create_refresh_button(parent, command, side="left", padx=(12, 0)):
    """
    Create a standardized refresh button.
    
    Args:
        parent: Parent widget
        command: Function to call when clicked
        side: Pack side (default: "left")
        padx: Padding x (default: (12, 0))
        
    Returns:
        The created button
    """
    button = ctk.CTkButton(
        parent,
        text="⟳ Refresh",
        command=command,
        height=32,
        width=120,
        fg_color=("gray70", "gray30"),
        hover_color=("gray60", "gray25")
    )
    button.pack(side=side, padx=padx)
    return button


def create_debounced_refresh(widget, callback, delay_ms=150):
    """
    Create a debounced refresh function for dropdowns.
    
    Args:
        widget: Widget to attach after() to (usually the card/content widget)
        callback: Function to call after debounce
        delay_ms: Delay in milliseconds (default: 150)
        
    Returns:
        Tuple of (refresh_timer dict, schedule_refresh function)
        
    Example:
        timer, schedule = create_debounced_refresh(card, update_display)
        dropdown.configure(command=schedule)
    """
    refresh_timer = {"id": None}
    
    def schedule_refresh(_choice=None):
        if refresh_timer["id"] is not None:
            try:
                widget.after_cancel(refresh_timer["id"])
            except Exception:
                pass
        refresh_timer["id"] = widget.after(delay_ms, callback)
    
    return refresh_timer, schedule_refresh


def create_popup_header_with_location(content):
    """
    Create a popup header with location dropdown.
    
    Args:
        content: Parent content widget
        
    Returns:
        Tuple of (header frame, location_dropdown widget)
    """
    from database_operations.repos import location_repository as location_repo
    
    header = ctk.CTkFrame(content, fg_color="transparent")
    header.pack(fill="x", padx=10, pady=(5, 10))
    
    ctk.CTkLabel(header, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))
    
    try:
        cities = ["All Locations"] + location_repo.get_all_cities()
    except Exception as e:
        print(f"Error loading cities: {e}")
        cities = ["All Locations"]
    
    location_dropdown = ctk.CTkComboBox(header, values=cities, width=220, font=("Arial", 13))
    location_dropdown.set("All Locations")
    location_dropdown.pack(side="left")
    
    return header, location_dropdown


# ============================= Visual Utilities =============================
def round_image_corners(image, radius):
    """Add rounded corners to an image."""
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
    """
    separator = ctk.CTkFrame(parent, height=2, fg_color="gray35")
    separator.pack(fill="x", pady=pady, padx=padx)
    return separator


def vertical_divider(parent, pady=5, padx=(0, 5)):
    """Add a vertical separator line.
    
    Args:
        parent: The parent container
        pady: Vertical padding (top, bottom)
        padx: Horizontal padding
    """
    separator = ctk.CTkFrame(parent, width=2, height=1, fg_color="gray35")
    separator.pack(fill="y", side="left", padx=padx, pady=pady)
    return separator
