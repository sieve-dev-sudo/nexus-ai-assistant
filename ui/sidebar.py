"""
ui/sidebar.py
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QFont

from LessonCodePython.theme import C, F
from ui.icons import python_logo_pixmap

TOPICS = [
    ("basic", "🔰 Basic"),
    ("variables", "📦 Variable && Data Types"),
    ("operators", "🔢 Operators"),
    ("conditional", "🔀 Conditional"),
    ("loop", "🔁 Loop"),
    ("array", "📋 Array"),
    ("function", "⚙️ Function"),
    ("data_structures", "🗂 Data Structures"),
    ("functions_advanced", "🔧 Functions Advanced"),
    ("file_handling", "📁 File Handling"),
    ("oop", "🏛 OOP"),
]


def _sidebar_width() -> int:
    font = QFont("Segoe UI", F["topic"])
    fm = QFontMetrics(font)
    widest = max(fm.horizontalAdvance(label) for _, label in TOPICS)
    return max(widest + 22 + 12 + 12 + 20, 340)


class Sidebar(QWidget):
    mode_changed = pyqtSignal(str)
    topic_selected = pyqtSignal(str)
    export_requested = pyqtSignal()
    clear_chat_requested = pyqtSignal()
    reset_progress_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(_sidebar_width())
        self.setStyleSheet(f"background:{C['bg_sidebar']};")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 14, 10, 14)
        root.setSpacing(4)

        # Title
        title_row = QWidget()
        title_lay = QHBoxLayout(title_row)
        title_lay.setContentsMargins(8, 6, 8, 10)
        title_lay.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(python_logo_pixmap(38))
        icon_lbl.setFixedSize(38, 38)
        title_lay.addWidget(icon_lbl)

        text_lbl = QLabel("Nexus AI")
        text_lbl.setStyleSheet(
            f"color:{C['brand_title']}; font-size:{F['title'] + 4}pt; "
            f"font-weight:700;"
        )
        title_lay.addWidget(text_lbl)
        title_lay.addStretch(1)

        root.addWidget(title_row)
        root.addWidget(self._hr())

        # Mode buttons
        root.addWidget(self._section_lbl("MODE"))
        self._btn_lesson = self._mk_btn("📚  Lesson", "lesson")
        self._btn_fix = self._mk_btn("🛠  Fix Code", "fix")
        root.addWidget(self._btn_lesson)
        root.addWidget(self._btn_fix)
        self._activate("lesson")
        root.addWidget(self._hr())

        # Topic container — tight, no extra spacing
        self._topic_outer = QWidget()
        self._topic_outer.setStyleSheet("background:transparent;")
        to_lay = QVBoxLayout(self._topic_outer)
        to_lay.setContentsMargins(0, 0, 0, 0)
        to_lay.setSpacing(0)
        to_lay.addWidget(self._section_lbl("TOPICS"))

        for key, label in TOPICS:
            b = QPushButton(label)
            b.setCursor(Qt.PointingHandCursor)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.setStyleSheet(self._topic_style())
            b.clicked.connect(lambda _, k=key: self.topic_selected.emit(k))
            to_lay.addWidget(b)

        to_lay.addStretch(0)

        scroll = QScrollArea()
        scroll.setWidget(self._topic_outer)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet(
            "QScrollArea { border:none; background:transparent; }"
            f"QScrollBar:vertical {{ background:transparent; width:4px; }}"
            f"QScrollBar::handle:vertical {{ background:{C['border']}; border-radius:2px; min-height:20px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}"
        )
        root.addWidget(scroll, stretch=1)

        # Export chat — always visible, bottom of sidebar
        root.addWidget(self._hr())
        export_btn = QPushButton("💾  Export Chat")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        export_btn.setStyleSheet(self._inactive_style())
        export_btn.clicked.connect(self.export_requested.emit)
        root.addWidget(export_btn)

        clear_btn = QPushButton("🗑️  Clear Chat")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        clear_btn.setStyleSheet(self._inactive_style())
        clear_btn.clicked.connect(self.clear_chat_requested.emit)
        root.addWidget(clear_btn)

        reset_btn = QPushButton("🔄  Reset Progress")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        reset_btn.setStyleSheet(self._inactive_style())
        reset_btn.clicked.connect(self.reset_progress_requested.emit)
        root.addWidget(reset_btn)

        settings_btn = QPushButton("⚙️  Settings")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        settings_btn.setStyleSheet(self._inactive_style())
        settings_btn.clicked.connect(self.settings_requested.emit)
        root.addWidget(settings_btn)

        # Developer credit — small, muted, centered
        credit_lbl = QLabel("Developed by Mr. Siev E")
        credit_lbl.setAlignment(Qt.AlignCenter)
        credit_lbl.setStyleSheet(
            f"color:{C['text_muted']}; font-size:{F['label']}pt; padding:8px 4px 2px;"
        )
        root.addWidget(credit_lbl)

    def _mk_btn(self, label, mode):
        btn = QPushButton(label)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setStyleSheet(self._inactive_style())
        btn.clicked.connect(lambda: self._on_mode(mode))
        return btn

    def _on_mode(self, mode):
        self._activate(mode)
        self.mode_changed.emit(mode)

    def _activate(self, mode):
        active = (
            f"QPushButton {{ background:{C['accent']}; color:#fff; "
            f"border:none; text-align:left; padding:9px 14px; "
            f"border-radius:8px; font-size:{F['sidebar']}pt; font-weight:600; }}"
        )
        self._btn_lesson.setStyleSheet(active if mode == "lesson" else self._inactive_style())
        self._btn_fix   .setStyleSheet(active if mode == "fix" else self._inactive_style())
        if hasattr(self, "_topic_outer"):
            self._topic_outer.setVisible(mode == "lesson")

    @staticmethod
    def _inactive_style():
        return (
            f"QPushButton {{ background:transparent; color:{C['text_secondary']}; "
            f"border:none; text-align:left; padding:9px 14px; "
            f"border-radius:8px; font-size:{F['sidebar']}pt; }}"
            f"QPushButton:hover {{ background:{C['bg_hover']}; color:{C['text_primary']}; }}"
        )

    @staticmethod
    def _topic_style():
        return (
            f"QPushButton {{ background:transparent; color:{C['text_secondary']}; "
            f"border:none; text-align:left; padding:7px 12px; "
            f"border-radius:6px; font-size:{F['topic']}pt; white-space:nowrap; }}"
            f"QPushButton:hover {{ background:{C['bg_hover']}; color:{C['text_primary']}; }}"
        )

    @staticmethod
    def _section_lbl(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color:{C['text_muted']}; font-size:{F['label']}pt; "
            f"font-weight:600; padding:8px 8px 4px; letter-spacing:1px;"
        )
        return lbl

    @staticmethod
    def _hr():
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setStyleSheet(f"background:{C['border']}; max-height:1px; margin:4px 0;")
        return f
