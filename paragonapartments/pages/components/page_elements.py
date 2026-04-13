"""Page elements aggregator module.

This module re-exports all UI components from specialized submodules for backward compatibility.
All files that import `pages.components.page_elements` will continue to work without changes.

Submodules:
- popup_utils/date_utils/style_utils/ui_controls_utils/image_utils/pdf_export_utils: Utility helpers
- ui_containers: Layout containers (content, scrollable, row)
- ui_cards: Card components (function card, popup, badges, stats)
- ui_forms: Form builder with validation and field types
- ui_tables: Data tables with CRUD operations and pagination

Usage:
    import pages.components.page_elements as pe
    
    # All functions from submodules are available directly:
    content = pe.ContentContainer(parent)
    button = pe.ActionButton(content, "Click Me", handle_click)
    table_builder = pe.DataTable(content, columns, data)
    table, refresh = table_builder.table_container, table_builder.refresh_table
"""

# Re-export all functions from specialized modules
# This maintains backward compatibility for existing imports

# Utilities: dates, buttons, patterns, visual elements
from .popup_utils import (
    center_popup,
    enable_click_outside_to_close,
)
from .date_utils import (
    parse_date_string,
    open_date_picker,
)
from .style_utils import (
    style_primary_button,
    style_accent_secondary_button,
    style_secondary_button,
    style_primary_dropdown,
    style_secondary_dropdown,
)
from .ui_controls_utils import (
    create_refresh_button,
    create_debounced_refresh,
    create_popup_header_with_location,
    normalize_location_value,
    content_separator,
    vertical_divider,
    create_dynamic_dropdown_with_refresh,
)
from .image_utils import (
    round_image_corners,
)
from .pdf_export_utils import (
    PDFReportExporter,
    PDFExportUI,
)

# Graph popup utilities: specialized functions for graph popups
from .graph_popup_utilities import GraphPopup

# Containers: layout and scrolling
from .ui_containers import (
    ContentContainer,
    ScrollableContainer,
    RowContainer,
)

# Cards: function cards, popups, badges, stats
from .ui_cards import (
    FunctionCard,
    ActionButton,
    PopupCard,
    InfoBadge,
    LocationDropdownWithLabel,
    StatCard,
    StatsGrid,
)

# Tabs: top navigation selectors
from .ui_tabs import DashboardTabsMenu

# Forms: form builder with validation
from .ui_forms import Form

# Tables: data tables with CRUD
from .ui_tables import (
    DataTable,
    EditableTablePopup,
    ViewableTablePopup,
)

# Export all for 'from page_elements import *'
__all__ = [
    # Utility functions
    'enable_click_outside_to_close',
    'center_popup',
    'parse_date_string',
    'open_date_picker',
    'style_primary_button',
    'style_accent_secondary_button',
    'style_secondary_button',
    'style_primary_dropdown',
    'style_secondary_dropdown',
    'create_refresh_button',
    'create_debounced_refresh',
    'create_popup_header_with_location',
    'normalize_location_value',
    'content_separator',
    'vertical_divider',
    'create_dynamic_dropdown_with_refresh',
    'round_image_corners',
    'PDFReportExporter',
    'PDFExportUI',
    'GraphPopup',
    # Containers
    'ContentContainer',
    'ScrollableContainer',
    'RowContainer',
    # Cards
    'FunctionCard',
    'ActionButton',
    'PopupCard',
    'InfoBadge',
    'LocationDropdownWithLabel',
    'StatCard',
    'StatsGrid',
    'DashboardTabsMenu',
    # Forms
    'Form',
    # Tables
    'DataTable',
    'EditableTablePopup',
    'ViewableTablePopup',
]
