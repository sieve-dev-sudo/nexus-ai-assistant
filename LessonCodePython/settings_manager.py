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


def load_settings(path: Path = SETTINGS_PATH) -> Dict[str, Any]:
    """Load saved settings from disk, filling in any missing keys with defaults."""
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            merged = dict(DEFAULTS)
            merged.update({k: v for k, v in data.items() if k in DEFAULTS})
            return merged
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
