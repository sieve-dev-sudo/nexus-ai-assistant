"""
ui/main_window.py
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget

from LessonCodePython.theme import C
from LessonCodePython.lesson_engine import LessonEngine
from FixCode.fix_code_engine import FixCodeEngine, INSTRUCTIONS as FIX_WELCOME
from ui.sidebar import Sidebar
from ui.chat_panel import ChatPanel
from ui.icons import python_logo_html_tag

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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus AI — Python Assistant")
        self.resize(1000, 720)
        self.setMinimumSize(800, 540)
        self._build()

    def _build(self):
        root = QWidget()
        root.setStyleSheet(f"background:{C['bg_main']};")
        self.setCentralWidget(root)

        lay = QHBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.mode_changed  .connect(self._switch_mode)
        self._sidebar.topic_selected.connect(self._on_topic)

        self._stack = QStackedWidget()

        self._lesson_panel = ChatPanel(LessonEngine(), welcome_text=LESSON_WELCOME)
        self._lesson_panel.set_placeholder("Ask a Python question…")

        self._fix_panel = ChatPanel(FixCodeEngine(), welcome_text=FIX_WELCOME)
        self._fix_panel.set_placeholder("Paste your Python code here to fix it…")

        self._stack.addWidget(self._lesson_panel)
        self._stack.addWidget(self._fix_panel)

        lay.addWidget(self._sidebar)
        lay.addWidget(self._stack)

    def _switch_mode(self, mode: str):
        self._stack.setCurrentIndex(0 if mode == "lesson" else 1)

    def _on_topic(self, key: str):
        self._stack.setCurrentIndex(0)
        self._lesson_panel.inject_text(
            TOPIC_QUESTIONS.get(key, f"Explain {key} in Python")
        )
