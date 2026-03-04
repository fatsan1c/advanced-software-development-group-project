"""Graph Popup Utilities - Reusable components for graph popups with controls."""

import customtkinter as ctk
import database_operations.repos.location_repository as location_repo
from .ui_utilities import (
    create_refresh_button, 
    create_debounced_refresh, 
    open_date_picker,
    create_export_pdf_button,
    show_pdf_export_success_popup,
    show_pdf_export_error_popup
)
from .config.theme import SECONDARY_GRAY, SECONDARY_GRAY_HOVER, TEXT_COLOR
import pages.components.pdf_export as pdf_export


def create_graph_popup_controls(content, include_location=True, default_location=None, 
                                get_date_range_func=None, date_range_params=None):
    """Create standardized graph popup controls.
    
    Returns dict with control widgets and helper functions.
    """
    controls = ctk.CTkFrame(content, fg_color="transparent")
    controls.pack(fill="x", padx=(10,0), pady=(5, 5))
    
    # Top row: location and grouping
    row_top = ctk.CTkFrame(controls, fg_color="transparent")
    row_top.pack(fill="x")
    
    # Location dropdown
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
    
    # Get default date range
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
                 fg_color=SECONDARY_GRAY, hover_color=SECONDARY_GRAY_HOVER, text_color=TEXT_COLOR).pack(side="left", padx=(6, 0))
    ctk.CTkButton(end_wrap, text="📅", width=34, height=28, font=("Arial", 13),
                 command=lambda: open_date_picker(end_entry, content.winfo_toplevel()),
                 fg_color=SECONDARY_GRAY, hover_color=SECONDARY_GRAY_HOVER, text_color=TEXT_COLOR).pack(side="left", padx=(6, 0))
    
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
    
    error_label = ctk.CTkLabel(content, text="", font=("Arial", 12), text_color="red", wraplength=900)
    graph_container = ctk.CTkFrame(content, fg_color="transparent")
    graph_container.pack(fill="both", expand=True)
    
    refresh_btn = create_refresh_button(row_top, command=lambda: None, side="left", padx=(18, 0))
    export_btn = create_export_pdf_button(
        row_dates,
        canvas_or_fig=None,
        default_filename="report",
        stats_text=None,
        title="Report",
        variant="popup"
    )
    
    return {
        'controls': controls,
        'location_dropdown': popup_location_dropdown,
        'grouping_dropdown': grouping_dropdown,
        'start_entry': start_entry,
        'end_entry': end_entry,
        'error_label': error_label,
        'graph_container': graph_container,
        'refresh_btn': refresh_btn,
        'export_btn': export_btn,
        'current_canvas': {'canvas': None},
        'apply_grouping_defaults': apply_grouping_defaults
    }


def setup_complete_graph_popup(controls, content, graph_function, location_mapper=None, fixed_location=None,
                               stats_generator=None, export_title="Report", export_filename="report"):
    """Set up graph popup with render function, bindings, and export."""
    location_dropdown = controls['location_dropdown']
    grouping_dropdown = controls['grouping_dropdown']
    start_entry = controls['start_entry']
    end_entry = controls['end_entry']
    error_label = controls['error_label']
    graph_container = controls['graph_container']
    refresh_btn = controls['refresh_btn']
    export_btn = controls['export_btn']
    current_canvas = controls['current_canvas']
    apply_grouping_defaults = controls['apply_grouping_defaults']
    
    def render_graph():
        for w in graph_container.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        
        try:
            if fixed_location:
                location = fixed_location
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
            
            if location is not None:
                canvas = graph_function(graph_container, location=location, start_date=start_date, 
                             end_date=end_date, grouping=grouping)
            else:
                canvas = graph_function(graph_container, start_date=start_date, 
                             end_date=end_date, grouping=grouping)
            
            current_canvas['canvas'] = canvas
            error_label.pack_forget()
        except Exception as e:
            error_label.configure(text=str(e))
            error_label.pack(fill="x", padx=10, pady=(0, 5), before=graph_container)
            current_canvas['canvas'] = None
    
    refresh_btn.configure(command=render_graph)
    refresh_timer, schedule_refresh = create_debounced_refresh(content, render_graph)
    
    if location_dropdown is not None:
        location_dropdown.configure(command=schedule_refresh)
    
    def on_grouping_change(choice=None):
        apply_grouping_defaults(grouping_dropdown.get())
        schedule_refresh(choice)
    grouping_dropdown.configure(command=on_grouping_change)
    
    start_entry.bind("<Return>", lambda e: schedule_refresh())
    start_entry.bind("<FocusOut>", lambda e: schedule_refresh())
    end_entry.bind("<Return>", lambda e: schedule_refresh())
    end_entry.bind("<FocusOut>", lambda e: schedule_refresh())
    
    render_graph()
    
    def handle_export():
        try:
            canvas = current_canvas['canvas']
            if canvas is None:
                raise ValueError("No chart available to export")
            
            fig = canvas.figure if hasattr(canvas, 'figure') else canvas
            stats = stats_generator() if stats_generator and callable(stats_generator) else None
            
            pdf_path = pdf_export.export_chart_to_pdf(
                fig,
                filename=export_filename,
                stats_text=stats,
                title=export_title
            )
            
            if pdf_path:
                show_pdf_export_success_popup(content.winfo_toplevel(), pdf_path)
        except Exception as e:
            show_pdf_export_error_popup(content.winfo_toplevel(), str(e))
    
    export_btn.configure(command=handle_export)


def open_graph_popup(parent, popup_title: str, button_text: str, graph_function,
                    include_location=True, default_location=None, get_date_range_func=None,
                    date_range_params=None, location_mapper=None, fixed_location=None,
                    include_export=True, stats_generator=None, export_title="Report",
                    export_filename="report", font_size=16):
    """Create a complete graph popup button with automatic setup.
    
    Combines popup creation, controls, and graph rendering into one call.
    Returns (button, export_button) if include_export=True, otherwise just button.
    """
    from .ui_cards import popup_card
    from .ui_utilities import style_primary_button
    
    if include_export:
        def generate_graph_for_export():
            temp_frame = ctk.CTkFrame(parent)
            evaluated_location = default_location() if callable(default_location) else default_location
            
            if date_range_params is not None:
                evaluated_params = date_range_params() if callable(date_range_params) else date_range_params
            elif evaluated_location and location_mapper:
                evaluated_params = location_mapper(evaluated_location)
            else:
                evaluated_params = evaluated_location
            
            if fixed_location:
                loc = fixed_location
            elif evaluated_location:
                loc = location_mapper(evaluated_location) if location_mapper else evaluated_location
            else:
                loc = None
            
            start_date = None
            end_date = None
            if get_date_range_func and evaluated_params is not None:
                try:
                    date_range = get_date_range_func(evaluated_params, grouping="month")
                    start_date = date_range.get("start_date")
                    end_date = date_range.get("end_date")
                except Exception:
                    pass
            
            if loc is not None:
                canvas = graph_function(temp_frame, location=loc, start_date=start_date, 
                                      end_date=end_date, grouping="month")
            else:
                canvas = graph_function(temp_frame, start_date=start_date, 
                                      end_date=end_date, grouping="month")
            
            temp_frame.destroy()
            return canvas.figure if hasattr(canvas, 'figure') else canvas
        
        button_container = ctk.CTkFrame(parent, fg_color="transparent")
        button_container.pack(fill="x", expand=True)
        
        popup_btn, open_popup_func = popup_card(button_container, title=popup_title, 
                                                button_text=button_text, button_size="full")
        
        popup_btn.pack_forget()
        popup_btn.pack(side="left", expand=True)
        
        inline_stats_generator = None
        if stats_generator:
            def inline_stats_generator():
                try:
                    evaluated_location = default_location() if callable(default_location) else default_location
                    
                    if fixed_location:
                        loc = fixed_location
                    elif evaluated_location:
                        loc = location_mapper(evaluated_location) if location_mapper else evaluated_location
                    else:
                        loc = None
                    
                    if callable(stats_generator):
                        try:
                            import inspect
                            sig = inspect.signature(stats_generator)
                            if len(sig.parameters) > 0:
                                return stats_generator(loc) if loc is not None else stats_generator()
                            else:
                                return stats_generator()
                        except (ValueError, TypeError):
                            return stats_generator()
                    return None
                except Exception:
                    return None
        
        export_btn = create_export_pdf_button(
            button_container,
            canvas_or_fig=generate_graph_for_export,
            default_filename=export_filename,
            stats_text=inline_stats_generator,
            title=export_title,
            variant="inline"
        )
    else:
        popup_btn, open_popup_func = popup_card(parent, title=popup_title, button_text=button_text,
                                                small=False, button_size="full")
        export_btn = None
    
    def setup_and_open_popup():
        content = open_popup_func()
        evaluated_location = default_location() if callable(default_location) else default_location
        
        if date_range_params is not None:
            evaluated_params = date_range_params() if callable(date_range_params) else date_range_params
        elif evaluated_location and location_mapper:
            evaluated_params = location_mapper(evaluated_location)
        else:
            evaluated_params = evaluated_location
        
        controls = create_graph_popup_controls(
            content,
            include_location=include_location,
            default_location=evaluated_location,
            get_date_range_func=get_date_range_func,
            date_range_params=evaluated_params
        )
        
        popup_stats_generator = None
        if stats_generator:
            def popup_stats_generator():
                try:
                    if fixed_location:
                        loc = fixed_location
                    elif controls['location_dropdown'] is not None:
                        loc_value = controls['location_dropdown'].get()
                        loc = location_mapper(loc_value) if location_mapper else loc_value
                    else:
                        loc = None
                    
                    if callable(stats_generator):
                        try:
                            import inspect
                            sig = inspect.signature(stats_generator)
                            if len(sig.parameters) > 0:
                                return stats_generator(loc) if loc is not None else stats_generator()
                            else:
                                return stats_generator()
                        except (ValueError, TypeError):
                            return stats_generator()
                    return None
                except Exception:
                    return None
        
        setup_complete_graph_popup(
            controls, content, graph_function,
            location_mapper=location_mapper,
            fixed_location=fixed_location,
            stats_generator=popup_stats_generator,
            export_title=export_title,
            export_filename=export_filename
        )
    
    popup_btn.configure(command=setup_and_open_popup)
    style_primary_button(popup_btn, font_size=font_size)
    
    return (popup_btn, export_btn) if include_export else popup_btn
