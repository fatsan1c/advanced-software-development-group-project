"""Contributors: Aaron Antal-Bento (23013693), Ahmed AlShamy (24045361)
Styling helper functions for CTk widgets."""

from customtkinter import ThemeManager

from pages.components.config.theme import THEME


def style_primary_button(button, font_size=14):
    """Apply primary button styling."""
    try:
        button.configure(
            height=40,
            font=("Arial", font_size, "bold"),
            corner_radius=THEME.radii.button,
            fg_color=(THEME.colors.primary_blue, THEME.colors.primary_blue),
            hover_color=(THEME.colors.primary_blue_hover, THEME.colors.primary_blue_hover),
        )
        button.pack_configure(fill="x", padx=6, pady=(2, 0))
    except Exception:
        pass


def style_accent_secondary_button(button, font_size=14):
    """Apply accent secondary button styling."""
    try:
        button.configure(
            height=40,
            font=("Arial", font_size, "bold"),
            corner_radius=THEME.radii.button,
            fg_color=(THEME.colors.primary_blue, THEME.colors.primary_blue),
            hover_color=(THEME.colors.primary_blue_hover, THEME.colors.primary_blue_hover),
        )
        button.pack_configure(pady=(4, 0))
    except Exception:
        pass


def style_secondary_button(button, font_size=13):
    """Apply secondary button styling."""
    try:
        button.configure(
            height=40,
            font=("Arial", font_size, "bold"),
            corner_radius=THEME.radii.button,
            fg_color=THEME.colors.secondary_gray,
            hover_color=THEME.colors.secondary_gray_hover,
            text_color=THEME.colors.text,
        )
        button.pack_configure(pady=(4, 0))
    except Exception:
        pass


def style_primary_dropdown(dropdown):
    """Apply primary dropdown styling."""
    try:
        dropdown.configure(
            corner_radius=THEME.radii.button,
            fg_color=(THEME.colors.primary_blue, THEME.colors.primary_blue),
            button_color=ThemeManager.theme["CTkOptionMenu"]["button_color"],
            button_hover_color=ThemeManager.theme["CTkOptionMenu"]["button_hover_color"],
        )
    except Exception:
        pass


def style_secondary_dropdown(dropdown):
    """Apply secondary dropdown styling."""
    try:
        dropdown.configure(
            corner_radius=THEME.radii.button,
            text_color=THEME.colors.text,
            fg_color=ThemeManager.theme["CTkComboBox"]["fg_color"],
            button_color=ThemeManager.theme["CTkComboBox"]["button_color"],
            button_hover_color=ThemeManager.theme["CTkComboBox"]["button_hover_color"],
        )
    except Exception:
        pass
