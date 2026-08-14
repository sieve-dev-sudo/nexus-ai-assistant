"""
ui/input_bar.py — Auto-growing textarea (up to 8 lines) + Send button.
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QTextEdit, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics

from LessonCodePython.theme import C, F


class InputBar(QWidget):
    submitted = pyqtSignal(str)

    def __init__(self, placeholder: str = "Type a message…", parent=None):
        super().__init__(parent)
        self._build(placeholder)

    def _build(self, placeholder: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        self._editor = _GrowingTextEdit(placeholder, self)
        self._editor.returnPressed.connect(self._on_send)

        self._btn = QPushButton("➤")
        self._btn.setFixedSize(44, 44)
        self._btn.setCursor(Qt.PointingHandCursor)
        self._btn.clicked.connect(self._on_send)
        self._btn.setStyleSheet(
            f"QPushButton {{ background:{C['accent']}; color:#fff; "
            f"border-radius:10px; font-size:18px; border:none; }}"
            f"QPushButton:hover    {{ background:{C['accent2']}; }}"
            f"QPushButton:disabled {{ background:{C['border']}; "
            f"                        color:{C['text_muted']}; }}"
        )

        layout.addWidget(self._editor)
        layout.addWidget(self._btn, alignment=Qt.AlignBottom)
        self.setStyleSheet(
            f"background:{C['bg_card']}; border-top:1px solid {C['border']};"
        )

    def _on_send(self):
        text = self._editor.toPlainText().strip()
        if text:
            self.submitted.emit(text)
            self._editor.clear()

    def set_enabled(self, enabled: bool):
        self._editor.setEnabled(enabled)
        self._btn.setEnabled(enabled)

    def set_placeholder(self, text: str):
        self._editor.setPlaceholderText(text)

    def focus(self):
        self._editor.setFocus()

    def clear_input(self):
        self._editor.clear()


class _GrowingTextEdit(QTextEdit):
    returnPressed = pyqtSignal()

    LINES_MIN = 2    # always show at least 2 lines
    LINES_MAX = 8    # grow up to 8 lines then scroll

    def __init__(self, placeholder: str, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        font = QFont("Segoe UI", F["input"])
        self.setFont(font)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Calculate line height from font metrics
        fm = QFontMetrics(font)
        self._lh = fm.height() + 4          # line height + small gap
        self._pad = 22                        # top+bottom padding inside box
        self._min_h = self._lh * self.LINES_MIN + self._pad
        self._max_h = self._lh * self.LINES_MAX + self._pad

        self.setFixedHeight(self._min_h)
        self.document().contentsChanged.connect(self._adjust)
        self.setStyleSheet(
            f"background:{C['bg_input']}; color:{C['text_primary']}; "
            f"border:1px solid {C['border']}; border-radius:10px; "
            f"padding:10px 14px; font-size:{F['input']}pt;"
        )

    def _adjust(self):
        doc_h = int(self.document().size().height())
        new_h = max(self._min_h, min(doc_h + self._pad, self._max_h))
        if self.height() != new_h:
            self.setFixedHeight(new_h)
            # Notify parent layout to resize
            if self.parentWidget():
                self.parentWidget().adjustSize()

    def keyPressEvent(self, event):
        if (event.key() in (Qt.Key_Return, Qt.Key_Enter)
                and not (event.modifiers() & Qt.ShiftModifier)):
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)
