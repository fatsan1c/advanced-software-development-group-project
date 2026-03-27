"""Popup helper functions."""


def enable_click_outside_to_close(popup, parent_window):
    """Enable closing a popup by clicking outside of it."""

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

    def on_popup_destroy(_event=None):
        try:
            parent_window.unbind("<Button-1>", binding_id)
        except Exception:
            pass

    popup.bind("<Destroy>", on_popup_destroy)


def center_popup(popup, width, height):
    """Center a popup on screen with fixed dimensions."""
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - (width // 2)
    y = (popup.winfo_screenheight() // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")
