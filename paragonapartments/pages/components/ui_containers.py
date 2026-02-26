"""
UI Containers - Basic container and layout elements.
"""

import customtkinter as ctk
from pages.components.auto_hide_scrollable_frame import AutoHideScrollableFrame


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


def scrollable_container(parent, expand=True, fill="both", pady=10, padx=10):
    """Create a scrollable container for content that may exceed visible area.
    
    Automatically hides scrollbar when all content fits on screen.
    
    Args:
        parent: The parent container
        expand: Whether container expands to fill space
        fill: Fill direction (x, y, both, none)
        pady: Vertical padding
        padx: Horizontal padding
        
    Returns:
        The scrollable container (add widgets directly to this)
    """
    scrollable = AutoHideScrollableFrame(parent, fg_color="transparent", scroll_speed=2)
    scrollable.pack(expand=expand, fill=fill, pady=pady, padx=padx)
    return scrollable


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
