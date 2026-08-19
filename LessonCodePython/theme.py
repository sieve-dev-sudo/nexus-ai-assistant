"""
LessonCodePython/theme.py
──────────────────────────
Central colour palette + font sizes for the whole application.
`C` and `F` are fixed dict objects (not reassigned) so that
`reload_theme()` can update their *contents* in place — every module
that did `from LessonCodePython.theme import C, F` already holds a
reference to these same dict objects, so mutating them is visible
everywhere immediately (no re-import needed).

Note: this only affects styles computed *after* the reload (widgets
built afterward, or ones that explicitly re-apply their stylesheet).
Already-built widgets keep whatever stylesheet string was baked in at
construction time — see MainWindow._rebuild_ui(), which is what
actually makes a theme change visible without an app restart.
"""
from typing import Dict
from LessonCodePython.settings_manager import load_settings

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

# Fixed dict objects — never reassigned, only mutated (see reload_theme).
C: Dict[str, str] = {}
F: Dict[str, int] = {}


def _colors_for(theme_name: str) -> Dict[str, str]:
    return LIGHT_COLORS if theme_name == "light" else DARK_COLORS


def _fonts_for(scale: float) -> Dict[str, int]:
    return {
        "title":   round(16 * scale),
        "body":    round(15 * scale),
        "code":    round(14 * scale),
        "sidebar": round(14 * scale),
        "topic":   round(13 * scale),
        "label":   round(11 * scale),
        "input":   round(15 * scale),
    }


def reload_theme() -> None:
    """Re-read settings.json and refresh C/F in place. Called on app
    startup and again whenever the user saves new Settings — pairs
    with MainWindow._rebuild_ui() to make the change visible without
    restarting the app."""
    settings = load_settings()
    C.clear()
    C.update(_colors_for(settings.get("theme", "dark")))
    F.clear()
    F.update(_fonts_for(settings.get("font_scale", 1.0)))


reload_theme()

# Backwards-compatible aliases some modules may still reference.
COLORS = C
FONTS = F


def build_palette():
    """Build a QPalette from the *current* C dict — used both at app
    startup and again after a live theme switch (see
    MainWindow._rebuild_ui). Imports PyQt5 lazily so this module stays
    importable in contexts (like plain pytest) that don't need Qt."""
    from PyQt5.QtGui import QPalette, QColor

    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(C["bg_main"]))
    pal.setColor(QPalette.WindowText,      QColor(C["text_primary"]))
    pal.setColor(QPalette.Base,            QColor(C["bg_input"]))
    pal.setColor(QPalette.AlternateBase,   QColor(C["bg_card"]))
    pal.setColor(QPalette.Text,            QColor(C["text_primary"]))
    pal.setColor(QPalette.ButtonText,      QColor(C["text_primary"]))
    pal.setColor(QPalette.Button,          QColor(C["bg_card"]))
    pal.setColor(QPalette.Highlight,       QColor(C["accent"]))
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    pal.setColor(QPalette.PlaceholderText, QColor(C["text_muted"]))
    return pal
