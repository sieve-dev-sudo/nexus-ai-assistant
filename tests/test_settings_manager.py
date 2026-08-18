"""
tests/test_settings_manager.py
─────────────────────────────────
Covers LessonCodePython/settings_manager.py — save/load round-trips,
default fallback, and graceful handling of a missing/corrupt file.
"""
import json
import tempfile
from pathlib import Path

from LessonCodePython.settings_manager import load_settings, save_settings, DEFAULTS


def test_load_settings_returns_defaults_when_file_missing():
    path = Path(tempfile.mkdtemp()) / "settings.json"
    assert load_settings(path=path) == DEFAULTS


def test_save_then_load_round_trip():
    path = Path(tempfile.mkdtemp()) / "settings.json"
    save_settings({"theme": "light", "font_scale": 1.2}, path=path)
    loaded = load_settings(path=path)
    assert loaded["theme"] == "light"
    assert loaded["font_scale"] == 1.2


def test_save_settings_creates_parent_directory():
    path = Path(tempfile.mkdtemp()) / "nested" / "dir" / "settings.json"
    ok = save_settings({"theme": "dark", "font_scale": 1.0}, path=path)
    assert ok is True
    assert path.exists()


def test_load_settings_ignores_unknown_keys():
    path = Path(tempfile.mkdtemp()) / "settings.json"
    path.write_text(json.dumps({"theme": "light", "bogus_key": 123}), encoding="utf-8")
    loaded = load_settings(path=path)
    assert "bogus_key" not in loaded
    assert loaded["theme"] == "light"
    assert loaded["font_scale"] == DEFAULTS["font_scale"]  # missing key filled in


def test_load_settings_recovers_from_corrupt_file():
    path = Path(tempfile.mkdtemp()) / "settings.json"
    path.write_text("{not valid json", encoding="utf-8")
    assert load_settings(path=path) == DEFAULTS


def test_save_settings_handles_unwritable_path_gracefully():
    # Make a plain file, then try to save "inside" it as if it were a
    # directory — mkdir() raises NotADirectoryError (an OSError subclass).
    tmp_dir = Path(tempfile.mkdtemp())
    blocking_file = tmp_dir / "not_a_directory"
    blocking_file.write_text("x", encoding="utf-8")
    bad_path = blocking_file / "settings.json"

    ok = save_settings({"theme": "dark", "font_scale": 1.0}, path=bad_path)
    assert ok is False
