"""UI Utilities - Helper functions for dates, buttons, styling, and common UI patterns."""

import customtkinter as ctk
from customtkinter import ThemeManager
from PIL import Image, ImageDraw
from datetime import datetime
import os
from pages.components.config.theme import PRIMARY_BLUE, PRIMARY_BLUE_HOVER, ROUND_BTN, TEXT_COLOR, SECONDARY_GRAY, SECONDARY_GRAY_HOVER
import pages.components.pdf_export as pdf_export

try:
    from tkcalendar import Calendar
except Exception:
    Calendar = None


def enable_click_outside_to_close(popup, parent_window):
    """Enable closing popup by clicking outside of it."""
    def check_click_outside(event):
        if popup.winfo_exists():
            popup_x = popup.winfo_x()
            popup_y = popup.winfo_y()
            popup_width = popup.winfo_width()
            popup_height = popup.winfo_height()
            click_x = event.x_root
            click_y = event.y_root
            
            outside_x = click_x < popup_x or click_x > popup_x + popup_width
            outside_y = click_y < popup_y or click_y > popup_y + popup_height
            
            if outside_x or outside_y:
                popup.destroy()
                parent_window.unbind("<Button-1>", binding_id)
    
    binding_id = parent_window.bind("<Button-1>", check_click_outside, add="+")
    
    def on_popup_destroy(event=None):
        try:
            parent_window.unbind("<Button-1>", binding_id)
        except Exception:
            pass
    
    popup.bind("<Destroy>", on_popup_destroy)


def parse_date_string(date_str):
    """Parse YYYY-MM-DD date string to date object."""
    s = (date_str or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def open_date_picker(entry_widget, parent_window):
    """Open calendar date picker popup for an entry widget."""
    popup = ctk.CTkToplevel(parent_window)
    popup.title("Select Date")
    popup.geometry("360x430")
    popup.resizable(False, False)
    popup.transient(parent_window)
    enable_click_outside_to_close(popup, parent_window)

    selected = parse_date_string(entry_widget.get()) or datetime.now().date()
    mode = str(ctk.get_appearance_mode()).lower()
    is_dark = mode == "dark"

    shell = ctk.CTkFrame(popup, corner_radius=12, fg_color=("#F3F4F6", "#1F232A"),
                        border_width=1, border_color=("#D8DCE2", "#2C313A"))
    shell.pack(fill="both", expand=True, padx=8, pady=8)

    ctk.CTkLabel(shell, text="Pick a Date", font=("Arial", 24, "bold"),
                text_color=("#22252B", "#E9ECF2")).pack(anchor="w", padx=12, pady=(12, 4))
    ctk.CTkLabel(shell, text="Format: YYYY-MM-DD", font=("Arial", 12),
                text_color=("#5E6672", "#AAB2BE")).pack(anchor="w", padx=12, pady=(0, 8))

    if Calendar is None:
        ctk.CTkLabel(shell, text="Calendar unavailable.\nInstall tkcalendar package.",
                    justify="center", font=("Arial", 12)).pack(pady=18)
        ctk.CTkButton(shell, text="Close", command=popup.destroy, width=120).pack(pady=(10, 0))
        return

    cal_kwargs = {
        "selectmode": "day",
        "date_pattern": "yyyy-mm-dd",
        "year": selected.year,
        "month": selected.month,
        "day": selected.day,
    }
    
    if is_dark:
        cal_kwargs.update({
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
        })
    else:
        cal_kwargs.update({
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
        })

    cal = Calendar(shell, **cal_kwargs, showweeknumbers=False)
    cal.pack(fill="both", expand=True, padx=12, pady=(4, 10))

    def apply_date():
        entry_widget.delete(0, "end")
        entry_widget.insert(0, cal.get_date())
        popup.destroy()

    btn_row = ctk.CTkFrame(shell, fg_color="transparent")
    btn_row.pack(fill="x", padx=10, pady=(0, 10))
    
    ctk.CTkButton(btn_row, text="Cancel", command=popup.destroy, width=104, height=34,
                 font=("Arial", 14), fg_color=SECONDARY_GRAY,
                 hover_color=SECONDARY_GRAY_HOVER).pack(side="left")
    ctk.CTkButton(btn_row, text="Use Date", command=apply_date, width=104, height=34,
                 font=("Arial", 14), fg_color=PRIMARY_BLUE,
                 hover_color=PRIMARY_BLUE_HOVER).pack(side="right")


def style_primary_button(button, font_size=14):
    """Apply primary button styling."""
    try:
        button.configure(
            height=40, font=("Arial", font_size, "bold"), corner_radius=ROUND_BTN,
            fg_color=(PRIMARY_BLUE, PRIMARY_BLUE), hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER)
        )
        button.pack_configure(fill="x", padx=6, pady=(2, 0))
    except Exception:
        pass

def style_accent_secondary_button(button, font_size=14):
    """Apply accent secondary button styling."""
    try:
        button.configure(
            height=40, font=("Arial", font_size, "bold"), corner_radius=ROUND_BTN,
            fg_color=(PRIMARY_BLUE, PRIMARY_BLUE), hover_color=(PRIMARY_BLUE_HOVER, PRIMARY_BLUE_HOVER)
        )
        button.pack_configure(pady=(4, 0))
    except Exception:
        pass

def style_secondary_button(button, font_size=13):
    """Apply secondary button styling."""
    try:
        button.configure(
            height=40, font=("Arial", font_size, "bold"), corner_radius=ROUND_BTN,
            fg_color=SECONDARY_GRAY, hover_color=SECONDARY_GRAY_HOVER, text_color=TEXT_COLOR
        )
        button.pack_configure(pady=(4, 0))
    except Exception:
        pass

def style_primary_dropdown(dropdown):
    """Apply primary dropdown styling."""
    try:
        dropdown.configure(
            corner_radius=ROUND_BTN, fg_color=(PRIMARY_BLUE, PRIMARY_BLUE),
            button_color=ThemeManager.theme["CTkOptionMenu"]["button_color"],
            button_hover_color=ThemeManager.theme["CTkOptionMenu"]["button_hover_color"]
        )
    except Exception:
        pass

def style_secondary_dropdown(dropdown):
    """Apply secondary dropdown styling."""
    try:
        dropdown.configure(
            corner_radius=ROUND_BTN, text_color=TEXT_COLOR,
            fg_color=ThemeManager.theme["CTkComboBox"]["fg_color"],
            button_color=ThemeManager.theme["CTkComboBox"]["button_color"],
            button_hover_color=ThemeManager.theme["CTkComboBox"]["button_hover_color"]
        )
    except Exception:
        pass


def create_refresh_button(parent, command, side="left", padx=(12, 0), square=False):
    """Create a standardized refresh button."""
    button = ctk.CTkButton(
        parent,
        text="⟳ Refresh" if not square else "⟳",
        command=command,
        height=30 if square else 32,
        width=30 if square else 120,
        fg_color=SECONDARY_GRAY,
        hover_color=SECONDARY_GRAY_HOVER,
        text_color=TEXT_COLOR,
    )
    button.pack(side=side, padx=padx)
    return button


def create_debounced_refresh(widget, callback, delay_ms=150):
    """Create a debounced refresh function for dropdowns.
    
    Returns tuple of (refresh_timer dict, schedule_refresh function).
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


def show_pdf_export_success_popup(parent_widget, pdf_path):
    """Show success popup after PDF export."""
    success_popup = ctk.CTkToplevel(parent_widget)
    success_popup.title("Export Successful")
    success_popup.geometry("400x170")
    success_popup.resizable(False, False)
    success_popup.transient(parent_widget)
    
    # Center the popup
    success_popup.update_idletasks()
    x = (success_popup.winfo_screenwidth() // 2) - (400 // 2)
    y = (success_popup.winfo_screenheight() // 2) - (170 // 2)
    success_popup.geometry(f"400x170+{x}+{y}")
    
    # Enable click outside to close
    enable_click_outside_to_close(success_popup, parent_widget)
    
    # Success message
    ctk.CTkLabel(
        success_popup,
        text="PDF Exported Successfully",
        font=("Arial", 16, "bold"),
        text_color="#2BA89A"
    ).pack(pady=(20, 10))
    
    # File path
    ctk.CTkLabel(
        success_popup,
        text=f"Saved to:\n{pdf_path}",
        font=("Arial", 11),
        wraplength=400
    ).pack(pady=(0, 15))
    
    # Button container
    button_frame = ctk.CTkFrame(success_popup, fg_color="transparent")
    button_frame.pack(pady=(0, 15))
    
    def open_pdf():
        try:
            os.startfile(pdf_path)
            success_popup.destroy()
        except Exception:
            # Fallback for non-Windows systems
            import subprocess
            try:
                subprocess.run(['xdg-open', pdf_path])
            except Exception:
                pass
    
    # Open button
    ctk.CTkButton(
        button_frame,
        text="Open",
        command=open_pdf,
        width=100,
        height=32,
        fg_color=PRIMARY_BLUE,
        hover_color=PRIMARY_BLUE_HOVER,
        corner_radius=ROUND_BTN
    ).pack(side="left", padx=(0, 10))
    
    # Close button
    ctk.CTkButton(
        button_frame,
        text="Close",
        command=success_popup.destroy,
        width=100,
        height=32,
        fg_color=SECONDARY_GRAY,
        hover_color=SECONDARY_GRAY_HOVER,
        corner_radius=ROUND_BTN
    ).pack(side="left")


def show_pdf_export_error_popup(parent_widget, error_message):
    """Show an error popup when PDF export fails.
    
    Args:
        parent_widget: Parent widget to attach the popup to (usually content.winfo_toplevel())
        error_message: Error message to display
    """
    error_popup = ctk.CTkToplevel(parent_widget)
    error_popup.title("Export Failed")
    error_popup.geometry("400x150")
    error_popup.resizable(False, False)
    error_popup.transient(parent_widget)
    
    # Center the popup
    error_popup.update_idletasks()
    x = (error_popup.winfo_screenwidth() // 2) - (400 // 2)
    y = (error_popup.winfo_screenheight() // 2) - (150 // 2)
    error_popup.geometry(f"400x150+{x}+{y}")
    
    # Enable click outside to close
    enable_click_outside_to_close(error_popup, parent_widget)
    
    # Error title
    ctk.CTkLabel(
        error_popup,
        text="Export Failed",
        font=("Arial", 16, "bold"),
        text_color="#C75B6D"
    ).pack(pady=(20, 10))
    
    # Error message
    ctk.CTkLabel(
        error_popup,
        text=f"Error: {error_message}",
        font=("Arial", 11),
        wraplength=350
    ).pack(pady=(0, 15))
    
    # OK button
    ctk.CTkButton(
        error_popup,
        text="OK",
        command=error_popup.destroy,
        width=100,
        height=32
    ).pack(pady=(0, 15))


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


def create_dynamic_dropdown_with_refresh(parent, data_fetcher, display_formatter=lambda x: (str(x), x),
                                         empty_message="No items available"):
    """Create a dropdown with dynamic data and refresh button.
    
    Args:
        parent: Parent container
        data_fetcher: Function that returns list of data dicts when called
        display_formatter: Function that takes a data dict and returns (display_string, value_dict)
        empty_message: Message to show when no data available
        
    Returns:
        Tuple of (dropdown_widget, data_map_dict, refresh_function)
    """
    # Container
    container = ctk.CTkFrame(parent, fg_color="transparent")
    container.pack(fill="x", padx=0, pady=0)
    
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
    create_refresh_button(container, refresh, side="left", padx=(5, 0), square=True)
    
    # Initial load
    refresh()
    
    return dropdown, data_map, refresh


def create_export_pdf_button(parent, canvas_or_fig=None, default_filename: str | None = None,
                             stats_text: str | None = None, title: str = "Report",
                             button_text: str = "Export to PDF", button_width: int = 180,
                             pady: int = 5, padx: int = 5, variant: str = "standard"):
    """Create a button that exports a chart to PDF when clicked.
    
    Args:
        parent: Parent widget for the button
        canvas_or_fig: Either a FigureCanvasTkAgg, matplotlib Figure object, callable returning one, or None
        default_filename: Default filename (without .pdf extension)
        stats_text: Optional statistics text to include on second page (can be string or callable)
        title: Title for the report
        button_text: Text to display on the button
        button_width: Width of the button in pixels
        pady: Vertical padding
        padx: Horizontal padding
        variant: Button style variant - "standard", "inline", or "popup"
        
    Returns:
        CTkButton: The export button widget
    """
    def handle_export():
        try:
            # Get canvas/figure (handle callables)
            if callable(canvas_or_fig):
                obj = canvas_or_fig()
            else:
                obj = canvas_or_fig
            
            # Get stats text (handle callable)
            stats = stats_text() if callable(stats_text) else stats_text
            
            # Extract figure if canvas was provided
            if hasattr(obj, 'figure'):
                fig = obj.figure
            else:
                fig = obj
            
            # Check if we have a valid figure
            if fig is None:
                raise ValueError("No chart available to export")
            
            # Export to PDF
            pdf_path = pdf_export.export_chart_to_pdf(fig, filename=default_filename,
                                                      stats_text=stats, title=title)
            
            if pdf_path:
                show_pdf_export_success_popup(parent.winfo_toplevel(), pdf_path)
                
        except Exception as e:
            show_pdf_export_error_popup(parent.winfo_toplevel(), str(e))
    
    # Use placeholder command if no canvas provided
    command = handle_export if canvas_or_fig is not None else lambda: None
    
    # Load upload icon for inline/popup variants
    upload_icon = None
    if variant in ("inline", "popup"):
        try:
            from pathlib import Path
            icons_dir = Path(__file__).parent.parent / "icons"
            upload_icon_path_light = icons_dir / "upload_icon.png"
            upload_icon_path_dark = icons_dir / "upload_icon_dark.png"
            
            upload_icon = ctk.CTkImage(
                light_image=Image.open(upload_icon_path_light),
                dark_image=Image.open(upload_icon_path_dark),
                size=(18, 18) if variant == "inline" else (16, 16)
            )
        except Exception as e:
            print(f"Warning: Could not load upload icon: {e}")
            upload_icon = None
    
    # Configure button based on variant
    if variant == "inline":
        button_config = {
            "master": parent,
            "text": "" if upload_icon else "↑",
            "command": command,
            "width": 40,
            "height": 40,
            "font": ("Arial", 14, "bold"),
            "corner_radius": ROUND_BTN,
            "fg_color": SECONDARY_GRAY,
            "hover_color": SECONDARY_GRAY_HOVER,
            "text_color": TEXT_COLOR
        }
        if upload_icon:
            button_config["image"] = upload_icon
        button = ctk.CTkButton(**button_config)
        button.pack(side="left", pady=0, padx=0)
        
    elif variant == "popup":
        button_config = {
            "master": parent,
            "text": "Export",
            "command": command,
            "width": 100,
            "height": 32,
            "font": ("Arial", 14, "bold"),
            "corner_radius": ROUND_BTN,
            "fg_color": SECONDARY_GRAY,
            "hover_color": SECONDARY_GRAY_HOVER,
            "text_color": TEXT_COLOR
        }
        if upload_icon:
            button_config["image"] = upload_icon
            button_config["compound"] = "left"
        button = ctk.CTkButton(**button_config)
        button.pack(side="right", pady=0, padx=0)
        
    else:  # standard
        button = ctk.CTkButton(
            parent,
            text=button_text,
            command=command,
            width=button_width,
            height=36,
            font=("Arial", 13),
            corner_radius=ROUND_BTN,
            fg_color=SECONDARY_GRAY,
            hover_color=SECONDARY_GRAY_HOVER,
            text_color=TEXT_COLOR
        )
        button.pack(pady=pady, padx=padx)
    
    return button
