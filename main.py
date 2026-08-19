#!/usr/bin/env python3
"""
main.py — Entry point for Nexus AI Python Assistant
Run:
    pip install -r requirements.txt
    python main.py
"""

import sys
from PyQt5.QtWidgets import QApplication

from LessonCodePython.theme import build_palette
from LessonCodePython.version import __version__
from ui.main_window import MainWindow
from ui.icons import python_logo_icon


def main():
    """Create the QApplication, apply the theme, show the main window, and run the event loop."""
    app = QApplication(sys.argv)
    app.setApplicationName("Nexus AI — Python Assistant")
    app.setApplicationVersion(__version__)
    app.setStyle("Fusion")
    app.setPalette(build_palette())
    app.setWindowIcon(python_logo_icon(256))
    win = MainWindow()
    win.setWindowTitle("Nexus AI — Python Assistant")
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
