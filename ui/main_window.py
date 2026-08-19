"""
ui/main_window.py
"""

from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
    QFileDialog, QMessageBox, QShortcut, QApplication,
)
from PyQt5.QtGui import QKeySequence

from LessonCodePython.theme import C, build_palette
from LessonCodePython.lesson_engine import LessonEngine
from FixCode.fix_code_engine import FixCodeEngine, INSTRUCTIONS as FIX_WELCOME
from ui.sidebar import Sidebar
from ui.chat_panel import ChatPanel
from ui.settings_dialog import SettingsDialog
from ui.about_dialog import AboutDialog

LESSON_WELCOME = (
    "សូមស្វាគមន៍មកកាន់ Python AI Assistant!<br>"
    "📚 Lesson Mode : វាយឈ្មោះ Topic ឬជ្រើសពី Sidebar<br>"
    "📝 វាយ /quiz ដើម្បីធ្វើតេស្តចំណេះដឹង<br>"
    "📊 វាយ /progress ដើម្បីមើលវឌ្ឍនភាពការសិក្សា<br>"
    "👉 វាយ /start ដើម្បីមើល README ពេញ"
)

TOPIC_QUESTIONS = {
    "basic":               "Teach me basic Python",
    "variables":           "Explain variables and data types in Python",
    "operators":           "Explain Python operators",
    "conditional":         "Explain conditional statements if elif else",
    "loop":                "Explain for  and while  in Python",
    "array":               "Explain Python lists and arrays",
    "function":            "Explain Python functions with examples",
    "data_structures":     "Explain Python data structures: list, tuple, set, dictionary",
    "functions_advanced":  "Explain Python advanced functions: args kwargs lambda",
    "file_handling":       "Explain Python file handling: read write append",
    "oop":                 "Explain Python OOP: class, object, inheritance",
}


class MainWindow(QMainWindow):
    """Top-level window: wires the sidebar, the Lesson/Fix Code chat panels, and keyboard shortcuts together."""
    def __init__(self):
        """Set up this widget's state and build its child widgets."""
        super().__init__()
        self.setWindowTitle("Nexus AI — Python Assistant")
        self.resize(1000, 720)
        self.setMinimumSize(800, 540)
        self._build()

    def _build(self):
        """Build."""
        root = QWidget()
        root.setStyleSheet(f"background:{C['bg_main']};")
        self.setCentralWidget(root)

        lay = QHBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.mode_changed  .connect(self._switch_mode)
        self._sidebar.topic_selected.connect(self._on_topic)
        self._sidebar.export_requested.connect(self._export_chat)
        self._sidebar.clear_chat_requested.connect(self._clear_chat)
        self._sidebar.reset_progress_requested.connect(self._reset_progress)
        self._sidebar.settings_requested.connect(self._open_settings)
        self._sidebar.about_requested.connect(self._open_about)

        self._stack = QStackedWidget()

        # Reuse the existing LessonEngine (and its progress/quiz state)
        # across a UI rebuild — only create a fresh one on first build.
        if not hasattr(self, "_lesson_engine"):
            self._lesson_engine = LessonEngine()
        self._lesson_panel = ChatPanel(self._lesson_engine, welcome_text=LESSON_WELCOME)
        self._lesson_panel.set_placeholder("Ask a Python question…")

        self._fix_panel = ChatPanel(FixCodeEngine(), welcome_text=FIX_WELCOME)
        self._fix_panel.set_placeholder("Paste your Python code here to fix it…")

        self._stack.addWidget(self._lesson_panel)
        self._stack.addWidget(self._fix_panel)

        lay.addWidget(self._sidebar)
        lay.addWidget(self._stack)

        self._setup_shortcuts()

    def _rebuild_ui(self) -> None:
        """Tear down and rebuild the whole central widget so a new
        theme/font-size setting is visible immediately, without an app
        restart. The Lesson engine instance (and its progress) is kept;
        only its UI wrapper is rebuilt, so in-flight chat text is lost
        the same way it already would be on a restart, but progress and
        settings are not."""
        saved_mode_index = self._stack.currentIndex()
        old_central = self.centralWidget()

        # Re-apply the app-wide QPalette too (menus, scrollbars, etc.
        # pull from this, not just our own stylesheets).
        app = QApplication.instance()
        if app is not None:
            app.setPalette(build_palette())

        self._build()

        self._stack.setCurrentIndex(saved_mode_index)
        self._sidebar.set_active_mode("lesson" if saved_mode_index == 0 else "fix")

        if old_central is not None:
            old_central.deleteLater()

    def _setup_shortcuts(self):
        # Ctrl+K — jump to the message input box, from anywhere in the window.
        """Setup shortcuts."""
        focus_sc = QShortcut(QKeySequence("Ctrl+K"), self)
        focus_sc.activated.connect(
            lambda: self._stack.currentWidget().focus_input()
        )

        # Esc — clear whatever's currently typed in the active input box.
        clear_sc = QShortcut(QKeySequence("Esc"), self)
        clear_sc.activated.connect(
            lambda: self._stack.currentWidget().clear_input()
        )

        # Ctrl+L — clear the current chat (same action as the sidebar button).
        clear_chat_sc = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_chat_sc.activated.connect(self._clear_chat)

        # Ctrl+, — open Settings (common convention across many apps).
        settings_sc = QShortcut(QKeySequence("Ctrl+,"), self)
        settings_sc.activated.connect(self._open_settings)

        # Ctrl+F — jump to the sidebar's topic search box.
        search_sc = QShortcut(QKeySequence("Ctrl+F"), self)
        search_sc.activated.connect(self._sidebar.focus_search)

    def _switch_mode(self, mode: str):
        """Switch mode."""
        self._stack.setCurrentIndex(0 if mode == "lesson" else 1)

    def _on_topic(self, key: str):
        """On topic."""
        self._stack.setCurrentIndex(0)
        self._lesson_panel.inject_text(
            TOPIC_QUESTIONS.get(key, f"Explain {key} in Python")
        )

    def _export_chat(self):
        """Export chat."""
        panel = self._stack.currentWidget()
        default_name = f"nexus_ai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Chat", default_name, "Markdown Files (*.md);;All Files (*)"
        )
        if not path:
            return  # user cancelled
        ok = panel.export_history(path)
        if ok:
            QMessageBox.information(self, "Export Chat", f"បាន Export ទៅ:\n{path}")
        else:
            QMessageBox.warning(self, "Export Chat", "Export មិនជោគជ័យទេ — សូមសាកល្បងម្តងទៀត។")

    def _clear_chat(self):
        """Clear chat."""
        panel = self._stack.currentWidget()
        reply = QMessageBox.question(
            self, "Clear Chat",
            "តើអ្នកប្រាកដថាចង់លុប conversation បច្ចុប្បន្នចោលទាំងអស់ទេ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            panel.clear_chat()

    def _reset_progress(self):
        """Reset progress."""
        reply = QMessageBox.question(
            self, "Reset Progress",
            "តើអ្នកប្រាកដថាចង់លុបវឌ្ឍនភាពការសិក្សាទាំងអស់ចោលទេ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._lesson_engine.reset_progress()
            QMessageBox.information(self, "Reset Progress", "វឌ្ឍនភាពត្រូវបានលុបចោលរួចរាល់។")

    def _open_settings(self):
        """Open settings."""
        dlg = SettingsDialog(self)
        dlg.theme_changed.connect(self._rebuild_ui)
        dlg.exec_()

    def _open_about(self) -> None:
        """Open the About dialog."""
        dlg = AboutDialog(self)
        dlg.exec_()
