import sys
from typing import Union, Tuple, Optional, Any
from customtkinter import CTkScrollableFrame

# Extends CTkScrollableFrame with auto-hide scrollbar and configurable scroll speed
class AutoHideScrollableFrame(CTkScrollableFrame):
    """A scrollable frame that automatically hides the scrollbar when content fits on screen.
    
    Extends CustomTkinter's CTkScrollableFrame with:
    - Auto-hide scrollbar functionality
    - Configurable scroll speed
    """
    
    def __init__(self,
                 master: Any,
                 width: int = 200,
                 height: int = 200,
                 corner_radius: Optional[Union[int, str]] = None,
                 border_width: Optional[Union[int, str]] = None,
                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 border_color: Optional[Union[str, Tuple[str, str]]] = None,
                 scrollbar_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 scrollbar_button_color: Optional[Union[str, Tuple[str, str]]] = None,
                 scrollbar_button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 scroll_speed: int = 1,
                 hide_scrollbar_when_loading: bool = False,
                 **kwargs):
        """
        Args:
            scroll_speed: Scroll increment multiplier (default: 1). Higher = faster scrolling.
            hide_scrollbar_when_loading: If True, hide scrollbar during initial content loading.
                    Use when loading content that is expected to fit within the container to prevent scrollbar flicker during load.
            **kwargs: Additional arguments passed to CTkScrollableFrame
        """
        self._scroll_speed = scroll_speed
        
        # Initialize parent
        super().__init__(
            master=master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            scrollbar_fg_color=scrollbar_fg_color,
            scrollbar_button_color=scrollbar_button_color,
            scrollbar_button_hover_color=scrollbar_button_hover_color,
            **kwargs
        )
        
        # Hide scrollbar initially to prevent flicker during load
        if hide_scrollbar_when_loading:
            self._scrollbar.grid_remove()

        # Apply custom scroll speed
        self._set_scroll_increments()
        
        # Rebind configure to add debouncing
        self.unbind("<Configure>")
        self.bind("<Configure>", self._on_frame_configure_debounced)
        
        # Wait for all content to load before showing scrollbar
        self.after_idle(self._finish_loading)
    
    def _finish_loading(self):
        """Called after initial content load to check scrollbar visibility."""
        self.update_idletasks()
        self._parent_canvas.configure(yscrollcommand=self._on_canvas_scroll_autohide)
    
    def _on_canvas_scroll_autohide(self, *args):
        """Handle scrollbar visibility based on scroll position."""
        self._scrollbar.set(*args)
        
        # Auto-hide scrollbar when all content is visible
        top, bottom = args
        if float(top) <= 0.0 and float(bottom) >= 1.0:
            self._scrollbar.grid_remove()
        else:
            # Show scrollbar
            border_spacing = self._apply_widget_scaling(
                self._parent_frame.cget("corner_radius") + self._parent_frame.cget("border_width")
            )
            self._scrollbar.grid(row=1, column=1, sticky="ns", pady=border_spacing)
    
    def _on_frame_configure_debounced(self, event):
        """Debounced frame configure to prevent flickering."""
        # Update scroll region immediately
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        
    def _set_scroll_increments(self):
        """Set scroll speed based on platform and user preference."""
        if sys.platform.startswith("win"):
            self._parent_canvas.configure(yscrollincrement=1 * self._scroll_speed)
        elif sys.platform == "darwin":
            self._parent_canvas.configure(yscrollincrement=8 * self._scroll_speed)
        else:
            self._parent_canvas.configure(yscrollincrement=4 * self._scroll_speed)
    
    def _mouse_wheel_all(self, event):
        """Handle mousewheel scrolling with auto-hide check."""
        # Check if widget still exists before accessing it
        try:
            if not self._scrollbar.winfo_exists():
                return
            # Only scroll if scrollbar is visible
            if not self._scrollbar.winfo_ismapped():
                return
        except Exception:
            # Widget was destroyed, stop processing
            return
        
        # Call parent implementation with scroll speed applied
        if self.check_if_master_is_canvas(event.widget):
            if sys.platform.startswith("win"):
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview("scroll", -int(event.delta / 6) * self._scroll_speed, "units")
            elif sys.platform == "darwin":
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview("scroll", -event.delta * self._scroll_speed, "units")
            else:
                if self._parent_canvas.yview() != (0.0, 1.0):
                    self._parent_canvas.yview("scroll", -event.delta * self._scroll_speed, "units")
    
    def configure(self, **kwargs):
        """Extended configure to support scroll_speed parameter."""
        if "scroll_speed" in kwargs:
            self._scroll_speed = kwargs.pop("scroll_speed")
            self._set_scroll_increments()
        
        # Pass remaining kwargs to parent
        super().configure(**kwargs)
    
    def cget(self, attribute_name: str):
        """Extended cget to support scroll_speed parameter."""
        if attribute_name == "scroll_speed":
            return self._scroll_speed
        else:
            return super().cget(attribute_name)
