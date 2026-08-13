"""
ui/message_bubble.py
"""

import re
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QSizePolicy, QTextEdit, QPushButton
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QFontMetrics, QGuiApplication

from LessonCodePython.theme import C, F
from ui.avatars import AvatarLabel, TypingDots


class CodeBlock(QTextEdit):
    """
    Read-only code block.
    Height is computed purely from font metrics × line count —
    no QTimer, no parent notification needed.
    sizeHint() is also overridden so Qt layout honours it correctly.
    """
    H_LINE_EXTRA = 4    # leading between lines
    V_PAD = 32   # top+bottom padding inside the box

    def __init__(self, code: str, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlainText(code)

        self._font = QFont("Courier New", F["code"])
        self.setFont(self._font)

        self.setLineWrapMode(QTextEdit.NoWrap)          # keep original lines
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.document().setDocumentMargin(4)

        # Code blocks always keep a fixed dark "code editor" look —
        # deliberately NOT tied to C['text_primary'] which flips to a
        # near-black value in light theme (that would make the text
        # invisible against this block's fixed dark background).
        self.setStyleSheet(
            "background:#0d0d14; color:#e8e8f0; "
            "border:1px solid #252535; border-radius:8px; "
            f"padding:8px 14px; font-size:{F['code']}pt;"
        )

        self._target_h = self._calc_height(code)
        self.setFixedHeight(self._target_h)

        # Copy button — floats over the top-right corner of the block.
        # Also fixed-dark-styled to match the code block regardless of
        # the app's light/dark theme setting.
        self._copy_btn = QPushButton("📋 Copy", self)
        self._copy_btn.setCursor(Qt.PointingHandCursor)
        self._copy_btn.setStyleSheet(
            "QPushButton { background:#15151c; "
            "color:#7878a0; border:1px solid #252535; "
            f"border-radius:6px; padding:2px 8px; font-size:{F['label']}pt; }}"
            "QPushButton:hover { background:#252535; }"
        )
        self._copy_btn.clicked.connect(self._copy_code)
        self._copy_btn.adjustSize()
        self._position_copy_button()

    def _position_copy_button(self):
        margin = 6
        self._copy_btn.move(
            max(self.width() - self._copy_btn.width() - margin, margin), margin
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_copy_button()

    def _copy_code(self):
        QGuiApplication.clipboard().setText(self.toPlainText())
        self._copy_btn.setText("✓ Copied")
        QTimer.singleShot(1200, lambda: self._copy_btn.setText("📋 Copy"))

    def _calc_height(self, code: str) -> int:
        fm = QFontMetrics(self._font)
        line_h = fm.height() + self.H_LINE_EXTRA
        lines = code.split("\n")
        n = max(len(lines), 1)
        h = line_h * n + self.V_PAD
        return max(min(h, 640), 40)

    def sizeHint(self) -> QSize:
        return QSize(self.width(), self._target_h)

    def minimumSizeHint(self) -> QSize:
        return QSize(200, self._target_h)


class MessageBubble(QWidget):
    def __init__(self, text: str = "", role: str = "ai",
                 is_typing: bool = False, parent=None):
        super().__init__(parent)
        self.role = role
        self._dots = None
        self._setup(text, is_typing)

    def _setup(self, text: str, is_typing: bool):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 6, 0, 6)
        outer.setSpacing(10)

        avatar = (AvatarLabel("You", C["bg_user_bubble"])
                  if self.role == "user"
                  else AvatarLabel("🤖", C["bg_card"]))

        content = QWidget()
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(6)

        if is_typing:
            self._dots = TypingDots()
            self._dots.start()
            frame = QWidget()
            frame.setStyleSheet(
                f"background:{C['bg_ai_bubble']}; border-radius:12px; "
                f"border:1px solid {C['border']};"
            )
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(14, 10, 14, 10)
            fl.addWidget(self._dots)
            fl.addStretch()
            vbox.addWidget(frame)
        else:
            self._render(text, vbox)

        if self.role == "user":
            outer.addStretch()
            outer.addWidget(content)
            outer.addWidget(avatar)
        else:
            outer.addWidget(avatar)
            outer.addWidget(content)
            outer.addStretch()

    def _render(self, text: str, layout: QVBoxLayout):
        parts = re.split(r"```(?:python|output|)?\n?(.*?)```",
                         text, flags=re.DOTALL)
        for idx, part in enumerate(parts):
            # remove BOM / zero-width characters that may cause a leading blank line
            part = re.sub(r'^[\uFEFF\u200B]+', '', part)
            part = part.strip()
            if not part:
                continue
            if idx % 2 == 1:
                layout.addWidget(CodeBlock(part))
            else:
                lbl = QLabel(part)
                lbl.setWordWrap(True)
                lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
                bg = C["bg_user_bubble"] if self.role == "user" else C["bg_ai_bubble"]
                fg = "#ffffff" if self.role == "user" else C["text_primary"]
                lbl.setStyleSheet(
                    f"background:{bg}; color:{fg}; "
                    f"border-radius:12px; padding:12px 16px; "
                    f"border:1px solid {C['border']}; "
                    f"font-size:{F['body']}pt; line-height:1.65;"
                )
                layout.addWidget(lbl)

    def stop_typing(self):
        if self._dots:
            self._dots.stop()
