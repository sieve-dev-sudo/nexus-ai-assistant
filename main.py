#!/usr/bin/env python3
"""
main.py — Entry point for Nexus AI Python Assistant
Run:
    pip install -r requirements.txt
    python main.py
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor

from LessonCodePython.theme import C
from ui.main_window import MainWindow
from ui.icons import python_logo_icon

__version__ = "1.0.0"


def build_dark_palette() -> QPalette:
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


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Nexus AI — Python Assistant")
    app.setApplicationVersion(__version__)
    app.setStyle("Fusion")
    app.setPalette(build_dark_palette())
    app.setWindowIcon(python_logo_icon(256))
    win = MainWindow()
    win.setWindowTitle("Nexus AI — Python Assistant")
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
