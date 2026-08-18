"""
LessonCodePython/version.py
────────────────────────────
Single source of truth for the app version. Kept in its own tiny
module (rather than in main.py) so that ui/ code — like the About
dialog — can import it without creating a circular import (main.py
imports ui.main_window, which would otherwise need to import back
from main.py).
"""

__version__ = "1.1.0"
