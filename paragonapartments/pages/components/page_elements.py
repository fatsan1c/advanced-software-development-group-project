"""Page elements aggregator module.

This module re-exports all UI components from specialized submodules for backward compatibility.
All files that import `pages.components.page_elements` will continue to work without changes.

Submodules:
- ui_utilities: Date utilities, button styling, UI patterns, visual elements
- ui_containers: Layout containers (content, scrollable, row)
- ui_cards: Card components (function card, popup, badges, stats)
- ui_forms: Form builder with validation and field types
- ui_tables: Data tables with CRUD operations and pagination

Usage:
    import pages.components.page_elements as pe
    
    # All functions from submodules are available directly:
    content = pe.content_container(parent)
    button = pe.action_button(content, "Click Me", handle_click)
    table, refresh = pe.data_table(content, columns, data)
"""

# Re-export all functions from specialized modules
# This maintains backward compatibility for existing imports

# Utilities: dates, buttons, patterns, visual elements
from .ui_utilities import (
    parse_date_string,
    open_date_picker,
    style_primary_button,
    style_accent_secondary_button,
    style_secondary_button,
    create_refresh_button,
    create_debounced_refresh,
    create_popup_header_with_location,
    round_image_corners,
    content_separator,
    vertical_divider,
    create_graph_popup_controls,
    setup_complete_graph_popup,
    create_dynamic_dropdown_with_refresh,
)

# Containers: layout and scrolling
from .ui_containers import (
    content_container,
    scrollable_container,
    row_container,
)

# Cards: function cards, popups, badges, stats
from .ui_cards import (
    function_card,
    action_button,
    popup_card,
    info_badge,
    location_dropdown_with_label,
    stat_card,
    stats_grid,
)

# Forms: form builder with validation
from .ui_forms import (
    form_element,
    styled_form_element,
)

# Tables: data tables with CRUD
from .ui_tables import (
    data_table,
    create_edit_popup_with_table,
)

# Export all for 'from page_elements import *'
__all__ = [
    # Utilities
    'parse_date_string',
    'open_date_picker',
    'style_primary_button',
    'style_accent_secondary_button',
    'style_secondary_button',
    'create_refresh_button',
    'create_debounced_refresh',
    'create_popup_header_with_location',
    'round_image_corners',
    'content_separator',
    'vertical_divider',
    'create_graph_popup_controls',
    'style_accent_secondary_button',
    # Containers
    'content_container',
    'scrollable_container',
    'row_container',
    # Cards
    'function_card',
    'action_button',
    'popup_card',
    'info_badge',
    'location_dropdown_with_label',
    'stat_card',
    'stats_grid',
    # Forms
    'form_element',
    'styled_form_element',
    # Tables
    'data_table',
    'create_edit_popup_with_table',
]
