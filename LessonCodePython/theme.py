"""
LessonCodePython/theme.py
──────────────────────────
Central colour palette + font sizes for the whole application.
Reads the saved theme/font-scale preference once at import time —
changing settings takes effect on the next app restart.
"""
from LessonCodePython.settings_manager import load_settings

_settings = load_settings()

DARK_COLORS = {
    "bg_main":        "#0a0a0e",
    "bg_sidebar":     "#0f0f14",
    "bg_card":        "#15151c",
    "bg_input":       "#1a1a23",
    "bg_hover":       "#1e1e28",
    "bg_user_bubble": "#1d4ed8",
    "bg_ai_bubble":   "#13131a",
    "accent":         "#3b82f6",
    "accent2":        "#2563eb",
    "accent_green":   "#10b981",
    "text_primary":   "#e8e8f0",
    "text_secondary": "#7878a0",
    "text_muted":     "#404058",
    "border":         "#252535",
    "border_focus":   "#3b82f6",
    "dot_1":          "#3b82f6",
    "dot_2":          "#6366f1",
    "dot_3":          "#8b5cf6",
    "shadow":         "#00000099",
    "python_yellow":  "#ffd343",
    "python_blue":    "#4584b6",
    "brand_title":    "#ffd343",  # sidebar "Nexus AI" title color
}

LIGHT_COLORS = {
    "bg_main":        "#f5f5f8",
    "bg_sidebar":     "#ececf2",
    "bg_card":        "#ffffff",
    "bg_input":       "#ffffff",
    "bg_hover":       "#e2e2ec",
    "bg_user_bubble": "#2563eb",
    "bg_ai_bubble":   "#ffffff",
    "accent":         "#2563eb",
    "accent2":        "#1d4ed8",
    "accent_green":   "#059669",
    "text_primary":   "#16161f",
    "text_secondary": "#5a5a72",
    "text_muted":     "#9a9ab0",
    "border":         "#d8d8e2",
    "border_focus":   "#2563eb",
    "dot_1":          "#2563eb",
    "dot_2":          "#4f46e5",
    "dot_3":          "#7c3aed",
    "shadow":         "#00000033",
    "python_yellow":  "#ffd343",
    "python_blue":    "#4584b6",
    "brand_title":    "#1d4ed8",  # blue reads much better than yellow on light bg
}

COLORS = LIGHT_COLORS if _settings.get("theme") == "light" else DARK_COLORS

_scale = _settings.get("font_scale", 1.0)
FONTS = {
    "title":   round(16 * _scale),
    "body":    round(15 * _scale),
    "code":    round(14 * _scale),
    "sidebar": round(14 * _scale),
    "topic":   round(13 * _scale),
    "label":   round(11 * _scale),
    "input":   round(15 * _scale),
}

C = COLORS
F = FONTS
