"""
LessonCodePython/settings_manager.py
──────────────────────────────────────
Persists user preferences (theme, font scale) to a local JSON file.
Loaded once at startup — theme.py reads this before building its
color/font dicts, and settings_dialog.py writes to it when the user
saves changes. Changes apply on next app restart (kept intentionally
simple: no runtime re-styling of every already-built widget).
"""
import json
from pathlib import Path
from typing import Dict, Any

SETTINGS_PATH = Path.home() / ".nexus_ai" / "settings.json"

DEFAULTS: Dict[str, Any] = {
    "theme": "dark",       # "dark" | "light"
    "font_scale": 1.0,     # 0.8 - 1.5
}


FONT_SCALE_MIN = 0.8
FONT_SCALE_MAX = 1.5


def _validated(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Replace any bad value (wrong type, out of range) with a safe one,
    so a hand-edited or corrupted settings.json can't crash the app at
    startup (theme.py reads these values at import time)."""
    clean = dict(DEFAULTS)

    if settings.get("theme") in ("dark", "light"):
        clean["theme"] = settings["theme"]

    scale = settings.get("font_scale")
    if isinstance(scale, (int, float)) and not isinstance(scale, bool):
        clean["font_scale"] = min(max(float(scale), FONT_SCALE_MIN), FONT_SCALE_MAX)

    return clean


def load_settings(path: Path = SETTINGS_PATH) -> Dict[str, Any]:
    """Load saved settings from disk, filling in any missing or invalid keys with defaults."""
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return _validated(data)
    except (OSError, ValueError):
        pass
    return dict(DEFAULTS)


def save_settings(settings: Dict[str, Any], path: Path = SETTINGS_PATH) -> bool:
    """Write settings to disk (best-effort — returns False rather than raising on failure)."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        return True
    except OSError:
        return False
