"""
Central theme configuration for the Paragon Apartments application.

This module provides a structured theme token system for colors, typography,
chart styles, spacing, and corner radii.

Design goal:
- New code can import one object (`THEME`) for consistency.
- Styling values are accessed through typed token groups.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


ColorPair: TypeAlias = tuple[str, str]
FontToken: TypeAlias = tuple[str, int] | tuple[str, int, str]


@dataclass(frozen=True)
class ColorTokens:
	"""Core app color tokens."""

	primary_blue: str = "#2F7FD8"
	primary_blue_hover: str = "#2569B3"

	secondary_gray: ColorPair = ("gray70", "gray25")
	secondary_gray_hover: ColorPair = ("gray75", "gray30")
	text: ColorPair = ("gray15", "gray92")
	disabled_text: str = "gray50"

	success: str = "#2BA89A"
	warning: str = "#D4955A"
	error: str = "#C75B6D"
	info: str = "#5B9FD4"

	surface_card: ColorPair = ("gray92", "gray17")
	border_subtle: str = "#D0D4DA"


@dataclass(frozen=True)
class RadiusTokens:
	"""Corner radii (in pixels)."""

	box: int = 16
	button: int = 14
	input: int = 12


@dataclass(frozen=True)
class TypographyTokens:
	"""Typography tokens for consistent font usage."""

	family: str = "Arial"

	heading_lg: FontToken = ("Arial", 24, "bold")
	heading_md: FontToken = ("Arial", 20, "bold")
	heading_sm: FontToken = ("Arial", 18, "bold")
	title: FontToken = ("Arial", 16, "bold")
	body_lg: FontToken = ("Arial", 14)
	body_md: FontToken = ("Arial", 13)
	body_sm: FontToken = ("Arial", 12)
	caption: FontToken = ("Arial", 11)


@dataclass(frozen=True)
class ChartTokens:
	"""Chart-specific style tokens."""

	background: str = "#F8F9FA"
	title: str = "#1A1D24"
	label: str = "#4A4F5C"

	accent_green: str = "#2BA89A"
	accent_red: str = "#C75B6D"
	accent_orange: str = "#D4955A"
	accent_blue: str = "#5B9FD4"

	grid_y: str = "#E2E5E9"
	grid_x: str = "#E8EAED"
	spine: str = "#A8ADB8"
	tick: str = "#5A5F6B"
	legend_edge: str = "#D0D4DA"
	bar_edge: str = "#FFFFFF"

	today_marker: str = "#E74C3C"
	kpi_ring: str = "#D9DBE0"
	kpi_label: str = "#5A5F69"


@dataclass(frozen=True)
class SpaceTokens:
	"""Common spacing tokens."""

	xs: int = 4
	sm: int = 8
	md: int = 12
	lg: int = 16
	xl: int = 20


@dataclass(frozen=True)
class AppTheme:
	"""Root theme object."""

	colors: ColorTokens = ColorTokens()
	radii: RadiusTokens = RadiusTokens()
	typography: TypographyTokens = TypographyTokens()
	charts: ChartTokens = ChartTokens()
	spacing: SpaceTokens = SpaceTokens()


# Preferred import target for new code.
THEME = AppTheme()

__all__ = [
	"ColorPair",
	"FontToken",
	"ColorTokens",
	"RadiusTokens",
	"TypographyTokens",
	"ChartTokens",
	"SpaceTokens",
	"AppTheme",
	"THEME",
]
