"""UI containers - basic container and layout elements."""

import customtkinter as ctk

from pages.components.auto_hide_scrollable_frame import AutoHideScrollableFrame


class ContentContainer(ctk.CTkFrame):
    """Container frame for page content with configurable margins and padding."""

    def __init__(
        self,
        parent,
        anchor=None,
        side=None,
        margin=10,
        marginx=None,
        marginy=None,
        padding=15,
        paddingx=None,
        paddingy=None,
        hasBG=True,
        expand=False,
        fill=None,
    ):
        if marginy is None:
            marginy = margin
        if marginx is None:
            marginx = margin
        if paddingy is None:
            paddingy = padding
        if paddingx is None:
            paddingx = padding

        super().__init__(parent, fg_color="transparent" if not hasBG else None)
        self.pack(
            expand=expand,
            fill=fill,
            anchor=anchor,
            side=side,
            padx=marginx,
            pady=marginy,
            ipadx=paddingx,
            ipady=paddingy,
        )


class ScrollableContainer(AutoHideScrollableFrame):
    """Scrollable container that auto-hides the scrollbar when content fits."""

    def __init__(
        self,
        parent,
        expand=True,
        fill="both",
        pady=10,
        padx=10,
        hide_scrollbar_when_loading=False,
    ):
        super().__init__(
            parent,
            fg_color="transparent",
            scroll_speed=2,
            hide_scrollbar_when_loading=hide_scrollbar_when_loading,
        )
        self.pack(expand=expand, fill=fill, pady=pady, padx=padx)


class RowContainer(ctk.CTkFrame):
    """Single row container for horizontal page layout sections."""

    def __init__(self, parent, pady=0):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="x", pady=pady, padx=10)
