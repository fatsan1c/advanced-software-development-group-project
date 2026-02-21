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
                 **kwargs):
        """
        Args:
            scroll_speed: Scroll increment multiplier (default: 1). Higher = faster scrolling.
            **kwargs: Additional arguments passed to CTkScrollableFrame
        """
        self._scroll_speed = scroll_speed
        self._pending_update = None
        self._is_loading = True  # Track initial load state
        
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
        
        # Hide scrollbar initially to prevent flickering during load
        self._scrollbar.grid_remove()
        
        # Override the scroll command to add auto-hide functionality
        self._parent_canvas.configure(yscrollcommand=self._on_canvas_scroll_autohide)
        
        # Apply custom scroll speed
        self._set_scroll_increments()
        
        # Rebind configure to add debouncing
        self.unbind("<Configure>")
        self.bind("<Configure>", self._on_frame_configure_debounced)
        
        # Wait for all content to load before showing scrollbar
        self.after_idle(self._finish_loading)
    
    def destroy(self):
        """Cleanup before destroying the widget."""
        if self._pending_update:
            self.after_cancel(self._pending_update)
            self._pending_update = None
        
        # Mark as destroyed to prevent further operations
        self._is_loading = True  # Prevent any pending visibility updates
        
        super().destroy()
    
    def _finish_loading(self):
        """Called after initial content load to check scrollbar visibility."""
        self._is_loading = False
        self.update_idletasks()
        self._update_scrollbar_visibility()
    
    def _on_canvas_scroll_autohide(self, *args):
        """Handle scrollbar visibility based on scroll position."""
        self._scrollbar.set(*args)
        
        # Don't show scrollbar during initial loading
        if self._is_loading:
            return
        
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
        
        # Skip visibility updates during initial load
        if self._is_loading:
            return
        
        # Cancel pending visibility update
        if self._pending_update:
            self.after_cancel(self._pending_update)
        
        # Wait for event loop to settle, then check visibility
        self._pending_update = self.after_idle(self._schedule_visibility_check)
    
    def _schedule_visibility_check(self):
        """Schedule visibility check after a short delay to ensure layout is complete."""
        self._pending_update = self.after(30, self._update_scrollbar_visibility)
    
    def _update_scrollbar_visibility(self):
        """Check if scrollbar should be visible after layout settles."""
        self._pending_update = None
        
        # Ensure layout is up to date
        self.update_idletasks()
        
        # Check if content fits in canvas
        if self._parent_canvas.yview() == (0.0, 1.0):
            self._scrollbar.grid_remove()
            self._parent_canvas.yview_moveto(0)
        else:
            # Only show scrollbar if not loading
            if not self._is_loading:
                border_spacing = self._apply_widget_scaling(
                    self._parent_frame.cget("corner_radius") + self._parent_frame.cget("border_width")
                )
                self._scrollbar.grid(row=1, column=1, sticky="ns", pady=border_spacing)
    
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
