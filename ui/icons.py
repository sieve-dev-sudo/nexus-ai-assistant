"""
ui/icons.py — Python logo icon loader.

Anthropic's copyright policy means Claude cannot reproduce the official
Python Software Foundation logo artwork (it's trademarked/copyrighted).
So this module works in two layers:

  1. If a real logo file exists at assets/python_logo.png (or .svg),
     it is loaded and used as-is — this is the recommended path if you
     want the exact official mark. Download it yourself from:
     https://www.python.org/community/logos/  (free to use to indicate
     software is built with Python, per the PSF trademark usage policy).

  2. Otherwise, falls back to a simple hand-drawn two-tone approximation
     (NOT a trace of the official artwork) using the python_blue /
     python_yellow colors already defined in theme.py.
"""

from pathlib import Path
import tempfile

from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtSvg import QSvgRenderer

from LessonCodePython.theme import C

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
_ASSET_CANDIDATES = [ASSETS_DIR / "python_logo.svg", ASSETS_DIR / "python_logo.png"]

_PYTHON_LOGO_SVG = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <rect x="30" y="15" width="110" height="55" rx="27" fill="{C['python_blue']}"/>
  <rect x="95" y="55" width="45" height="80" rx="22" fill="{C['python_blue']}"/>
  <circle cx="65" cy="42" r="9" fill="#ffffff"/>

  <rect x="60" y="65" width="45" height="80" rx="22" fill="{C['python_yellow']}"/>
  <rect x="60" y="130" width="110" height="55" rx="27" fill="{C['python_yellow']}"/>
  <circle cx="135" cy="158" r="9" fill="#ffffff"/>
</svg>
""".strip()


def _draw_fallback(size: int) -> QPixmap:
    """Draw fallback."""
    renderer = QSvgRenderer(QByteArray(_PYTHON_LOGO_SVG.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()
    return pixmap


def python_logo_pixmap(size: int = 32) -> QPixmap:
    """Return the official logo if present in assets/, else a fallback."""
    for path in _ASSET_CANDIDATES:
        if path.exists():
            if path.suffix == ".svg":
                renderer = QSvgRenderer(str(path))
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                renderer.render(painter)
                painter.end()
                return pixmap
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                return pixmap.scaled(
                    size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
    return _draw_fallback(size)


def python_logo_icon(size: int = 64) -> QIcon:
    """Same logo as a QIcon, for window/taskbar icons."""
    return QIcon(python_logo_pixmap(size))


_cache_path = None


def python_logo_file_path(size: int = 40) -> str:
    """
    Return an on-disk PNG path for the logo — needed for embedding it
    inline inside rich-text QLabels via <img src="...">, since that
    requires a real file path (an in-memory QPixmap won't do).

    Uses the real asset if present; otherwise rasterises the fallback
    once into a small cache file under the system temp dir and reuses
    that path on subsequent calls.
    """
    for path in _ASSET_CANDIDATES:
        if path.exists() and path.suffix == ".png":
            return str(path)

    global _cache_path
    if _cache_path and Path(_cache_path).exists():
        return _cache_path

    pixmap = python_logo_pixmap(size)
    cache_file = Path(tempfile.gettempdir()) / f"nexus_ai_python_logo_{size}.png"
    pixmap.save(str(cache_file))
    _cache_path = str(cache_file)
    return _cache_path


def python_logo_html_tag(size: int = 20) -> str:
    """An <img> tag referencing the logo, for use inside rich-text QLabels."""
    uri = Path(python_logo_file_path(size)).as_uri()
    return (
        f'<img src="{uri}" width="{size}" height="{size}" '
        f'style="vertical-align:middle;">'
    )
