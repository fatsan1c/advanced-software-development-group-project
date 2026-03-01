"""
UI Utilities - Helper functions for dates, buttons, and common patterns.
"""

import customtkinter as ctk
from customtkinter import ThemeManager
from PIL import Image, ImageDraw
from datetime import datetime
from pages.components.config.theme import PRIMARY_BLUE, PRIMARY_BLUE_HOVER, ROUND_BTN

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

def style_accent_secondary_button(button, font_size=14):
    """
    Apply accent secondary button styling (for secondary actions like "viewtable").
    
    Args:
        button: CTkButton widget to style
        font_size: Font size for button text (default: 14)
    """
    try:
        button.configure(
            height=40,
            font=("Arial", font_size, "bold"),
            corner_radius=ROUND_BTN,
            fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
            hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER),
        )
        button.pack_configure(pady=(4, 0))
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

def style_primary_dropdown(dropdown):
    """
    Apply primary dropdown styling.
    
    Args:
        dropdown: CTkComboBox or CTkOptionMenu widget to style
    """
    try:
        dropdown.configure(
            corner_radius=ROUND_BTN,
            fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
            button_color=ThemeManager.theme["CTkOptionMenu"]["button_color"],
            button_hover_color=ThemeManager.theme["CTkOptionMenu"]["button_hover_color"]
        )
    except Exception:
        pass

def style_secondary_dropdown(dropdown):
    """
    Apply secondary dropdown styling.
    
    Args:
        dropdown: CtkComboBox or CtkOptionMenu widget to style
    """
    try:
        dropdown.configure(
            corner_radius=ROUND_BTN,
            fg_color=("gray85", "gray25"),
            button_color=ThemeManager.theme["CTkComboBox"]["button_color"],
            button_hover_color=ThemeManager.theme["CTkComboBox"]["button_hover_color"],
            text_color=("gray15", "gray92"),
        )
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


# ============================= Graph Popup Components =============================
def create_graph_popup_controls(content, include_location=True, default_location=None, 
                                get_date_range_func=None, date_range_params=None):
    """Create standardized graph popup controls (location, grouping, date range).
    
    This creates the common control panel structure used across Manager, Administrator, 
    and Finance Manager graph popups with location selector, grouping dropdown, 
    and date range inputs with date pickers.
    
    Args:
        content: Parent container for the controls
        include_location: Whether to include location dropdown (default: True)
        default_location: Default location value (default: "All Locations")
        get_date_range_func: Function to get default date range. Should accept 
                            (location, grouping) and return dict with start_date/end_date
        date_range_params: Additional params to pass to get_date_range_func (e.g., location)
        
    Returns:
        dict with keys:
            - 'controls': Main controls frame
            - 'location_dropdown': Location dropdown widget (if include_location=True)
            - 'grouping_dropdown': Grouping dropdown widget
            - 'start_entry': Start date entry widget
            - 'end_entry': End date entry widget
            - 'error_label': Error message label
            - 'graph_container': Container for the graph
            - 'refresh_btn': Refresh button widget
            - 'apply_grouping_defaults': Function to update dates based on grouping
    """
    import database_operations.repos.location_repository as location_repo
    
    # Controls container
    controls = ctk.CTkFrame(content, fg_color="transparent")
    controls.pack(fill="x", padx=10, pady=(5, 10))
    
    # Top row: location and grouping
    row_top = ctk.CTkFrame(controls, fg_color="transparent")
    row_top.pack(fill="x")
    
    # Location dropdown (optional)
    popup_location_dropdown = None
    if include_location:
        ctk.CTkLabel(row_top, text="Location:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 8))
        popup_cities = ["All Locations"] + location_repo.get_all_cities()
        popup_location_dropdown = ctk.CTkComboBox(row_top, values=popup_cities, width=220, font=("Arial", 13))
        popup_location_dropdown.set(default_location or "All Locations")
        popup_location_dropdown.pack(side="left")
    
    # Grouping dropdown
    label_padx = (18, 8) if include_location else (0, 8)
    ctk.CTkLabel(row_top, text="Grouping:", font=("Arial", 14, "bold")).pack(side="left", padx=label_padx)
    grouping_dropdown = ctk.CTkComboBox(row_top, values=["Monthly", "Yearly"], width=140, font=("Arial", 13))
    grouping_dropdown.set("Monthly")
    grouping_dropdown.pack(side="left")
    
    # Date range row
    row_dates = ctk.CTkFrame(controls, fg_color="transparent")
    row_dates.pack(fill="x", pady=(10, 0))
    
    # Get default date range if function provided
    default_start = ""
    default_end = ""
    if get_date_range_func and date_range_params is not None:
        try:
            default_range = get_date_range_func(date_range_params, grouping="month")
            default_start = default_range.get("start_date", "")
            default_end = default_range.get("end_date", "")
        except Exception as e:
            print(f"Error getting default date range: {e}")
    
    # Start date
    ctk.CTkLabel(row_dates, text="Start (YYYY-MM-DD):", font=("Arial", 13, "bold")).pack(side="left", padx=(0, 8))
    start_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
    start_wrap.pack(side="left")
    start_entry = ctk.CTkEntry(start_wrap, width=140, font=("Arial", 13))
    if default_start:
        start_entry.insert(0, default_start)
    start_entry.pack(side="left")
    
    # End date
    ctk.CTkLabel(row_dates, text="End (YYYY-MM-DD):", font=("Arial", 13, "bold")).pack(side="left", padx=(18, 8))
    end_wrap = ctk.CTkFrame(row_dates, fg_color="transparent")
    end_wrap.pack(side="left")
    end_entry = ctk.CTkEntry(end_wrap, width=140, font=("Arial", 13))
    if default_end:
        end_entry.insert(0, default_end)
    end_entry.pack(side="left")
    
    # Date picker buttons
    ctk.CTkButton(start_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                 command=lambda: open_date_picker(start_entry, content.winfo_toplevel()),
                 fg_color=("gray80", "gray25"), hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))
    ctk.CTkButton(end_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                 command=lambda: open_date_picker(end_entry, content.winfo_toplevel()),
                 fg_color=("gray80", "gray25"), hover_color=("gray70", "gray30")).pack(side="left", padx=(6, 0))
    
    # Function to apply grouping defaults
    def apply_grouping_defaults(grouping_value):
        """Update date range based on grouping selection."""
        if not get_date_range_func or date_range_params is None:
            return
        gv = (grouping_value or "").strip().lower()
        g = "year" if gv.startswith("year") else "month"
        try:
            rng = get_date_range_func(date_range_params, grouping=g)
            start_entry.delete(0, "end")
            end_entry.delete(0, "end")
            if rng.get("start_date"):
                start_entry.insert(0, rng["start_date"])
            if rng.get("end_date"):
                end_entry.insert(0, rng["end_date"])
        except Exception as e:
            print(f"Error applying grouping defaults: {e}")
    
    # Error label
    error_label = ctk.CTkLabel(content, text="", font=("Arial", 12), text_color="red", wraplength=900)
    
    # Graph container
    graph_container = ctk.CTkFrame(content, fg_color="transparent")
    graph_container.pack(fill="both", expand=True)
    
    # Refresh button (to be added to row_top by caller)
    refresh_btn = ctk.CTkButton(row_top, text="⟳ Refresh", height=32, width=120,
                                fg_color=("gray70", "gray30"), hover_color=("gray60", "gray25"))
    refresh_btn.pack(side="left", padx=(18, 0))
    
    return {
        'controls': controls,
        'location_dropdown': popup_location_dropdown,
        'grouping_dropdown': grouping_dropdown,
        'start_entry': start_entry,
        'end_entry': end_entry,
        'error_label': error_label,
        'graph_container': graph_container,
        'refresh_btn': refresh_btn,
        'apply_grouping_defaults': apply_grouping_defaults
    }


def setup_complete_graph_popup(controls, content, graph_function, location_mapper=None, fixed_location=None):
    """Set up complete graph popup with render function, bindings, and auto-refresh.
    
    This handles the common graph rendering logic used across all graph popups,
    including error handling, debounced refresh, and event bindings.
    
    Args:
        controls: Dict returned from create_graph_popup_controls
        content: Parent content widget for debounced refresh
        graph_function: Function to create the graph. Should accept (container, location, start_date, end_date, grouping)
        location_mapper: Optional function to map location dropdown value to location parameter
        fixed_location: Optional fixed location value to use instead of dropdown value
    Example:
        controls = pe.create_graph_popup_controls(content, ...)
        pe.setup_complete_graph_popup(
            controls, content,
            graph_function=finance_repo.create_collected_trend_graph,
            location_mapper=lambda val: "all" if val == "All Locations" else val
        )
    """
    location_dropdown = controls['location_dropdown']
    grouping_dropdown = controls['grouping_dropdown']
    start_entry = controls['start_entry']
    end_entry = controls['end_entry']
    error_label = controls['error_label']
    graph_container = controls['graph_container']
    refresh_btn = controls['refresh_btn']
    apply_grouping_defaults = controls['apply_grouping_defaults']
    
    def render_graph():
        # Clear previous graph widgets/canvases
        for w in graph_container.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        
        try:
            if fixed_location:
                location = fixed_location
            # Get parameters
            elif location_dropdown is not None:
                location = location_dropdown.get()
                if location_mapper:
                    location = location_mapper(location)
            else:
                location = None
            
            start_date = start_entry.get().strip() or None
            end_date = end_entry.get().strip() or None
            
            grouping_value = (grouping_dropdown.get() or "Monthly").strip().lower()
            grouping = "year" if grouping_value.startswith("year") else "month"
            
            # Call graph function
            if location is not None:
                graph_function(graph_container, location=location, start_date=start_date, 
                             end_date=end_date, grouping=grouping)
            else:
                graph_function(graph_container, start_date=start_date, 
                             end_date=end_date, grouping=grouping)
            
            error_label.pack_forget()
        except Exception as e:
            error_label.configure(text=str(e))
            error_label.pack(fill="x", padx=10, pady=(0, 5), before=graph_container)
    
    # Set up refresh button
    refresh_btn.configure(command=render_graph)
    
    # Auto-refresh with debounce
    refresh_timer, schedule_refresh = create_debounced_refresh(content, render_graph)
    
    # Bind location dropdown if present
    if location_dropdown is not None:
        location_dropdown.configure(command=schedule_refresh)
    
    # Bind grouping dropdown with defaults update
    def on_grouping_change(choice=None):
        apply_grouping_defaults(grouping_dropdown.get())
        schedule_refresh(choice)
    grouping_dropdown.configure(command=on_grouping_change)
    
    # Bind date entries to refresh on Enter or focus out
    start_entry.bind("<Return>", lambda e: schedule_refresh())
    start_entry.bind("<FocusOut>", lambda e: schedule_refresh())
    end_entry.bind("<Return>", lambda e: schedule_refresh())
    end_entry.bind("<FocusOut>", lambda e: schedule_refresh())
    
    # Initial render
    render_graph()


def create_dynamic_dropdown_with_refresh(parent, label, data_fetcher, display_formatter, 
                                         empty_message="No items available"):
    """Create a dropdown with dynamic data and refresh button.
    
    This creates the common pattern of a labeled dropdown that fetches data dynamically
    and includes a refresh button to reload the data.
    
    Args:
        parent: Parent container
        label: Label text for the dropdown
        data_fetcher: Function that returns list of data dicts when called
        display_formatter: Function that takes a data dict and returns (display_string, value_dict)
        empty_message: Message to show when no data available
        width: Width of the dropdown (default: 400)
        
    Returns:
        Tuple of (dropdown_widget, data_map_dict, refresh_function)
        
    Example:
        def fetch_requests():
            return maintenance_repo.get_maintenance_requests(location="all", completed=0)
        
        def format_request(req):
            display = f"ID {req['request_ID']}: {req['issue_description'][:40]}"
            return (display, req['request_ID'])
        
        dropdown, data_map, refresh = create_dynamic_dropdown_with_refresh(
            parent, "Select Request:", fetch_requests, format_request
        )
    """
    # Container
    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(fill="x", padx=10, pady=(10, 0))
    
    # Label
    ctk.CTkLabel(container, text=label, font=("Arial", 13, "bold")).pack(pady=(0, 5))
    
    # Dropdown
    dropdown = ctk.CTkOptionMenu(
        container,
        values=["Loading..."],
        font=("Arial", 12)
    )
    dropdown.pack(side="left", expand=True, fill="x", pady=0)
    style_secondary_dropdown(dropdown)
    
    # Data map storage
    data_map = {}
    
    # Refresh function
    def refresh():
        try:
            data = data_fetcher()
            
            if not data:
                dropdown.configure(values=[empty_message])
                dropdown.set(empty_message)
                data_map.clear()
                return
            
            options = []
            data_map.clear()
            for item in data:
                display, value = display_formatter(item)
                options.append(display)
                data_map[display] = value
            
            dropdown.configure(values=options)
            dropdown.set(options[0])
        except Exception as e:
            dropdown.configure(values=[f"Error: {str(e)}"])
            dropdown.set(f"Error: {str(e)}")
            data_map.clear()
    
    # Refresh button
    create_refresh_button(container, refresh, side="left", padx=(10, 0))
    
    # Initial load
    refresh()
    
    return dropdown, data_map, refresh
