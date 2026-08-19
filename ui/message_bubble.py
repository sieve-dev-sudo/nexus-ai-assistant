"""
ui/message_bubble.py
"""

import re
import keyword as _keyword_module
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QSizePolicy, QTextEdit, QPushButton
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import (
    QFont, QFontMetrics, QGuiApplication,
    QSyntaxHighlighter, QTextCharFormat, QColor,
)

from LessonCodePython.theme import C, F
from ui.avatars import AvatarLabel, TypingDots


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Lightweight single-pass Python syntax highlighter for CodeBlock.

    Uses fixed, VS-Code-Dark-inspired colors (independent of the app's
    Dark/Light theme setting) since CodeBlock itself always keeps a
    fixed dark "code editor" background regardless of theme — see the
    note in CodeBlock.__init__.

    Known limitation: matching is done one line at a time, so a
    triple-quoted string that spans multiple lines won't be colored
    as a string past its first line. Good enough for the short
    snippets Fix Code / Lesson mode actually produces.
    """

    _BUILTINS = (
        "print len range int float str bool list tuple set dict type "
        "isinstance open input enumerate zip map filter sorted sum min "
        "max abs round self super None True False"
    ).split()

    def __init__(self, document):
        """Build the fixed set of (regex, format) highlighting rules."""
        super().__init__(document)

        def fmt(color: str, bold: bool = False) -> QTextCharFormat:
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold:
                f.setFontWeight(QFont.Bold)
            return f

        kw_pattern = r'\b(' + '|'.join(_keyword_module.kwlist) + r')\b'
        builtin_pattern = r'\b(' + '|'.join(self._BUILTINS) + r')\b'

        # Order matters: later rules paint OVER earlier ones on overlap,
        # so strings win over keyword-looking text inside them, and
        # comments win over everything (applied last).
        self._rules = [
            (re.compile(kw_pattern), fmt("#569cd6", bold=True)),
            (re.compile(builtin_pattern), fmt("#4ec9b0")),
            (re.compile(r'\b\d+\.?\d*\b'), fmt("#b5cea8")),
            (re.compile(r"'[^'\\]*(?:\\.[^'\\]*)*'"), fmt("#ce9178")),
            (re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"'), fmt("#ce9178")),
            (re.compile(r'#.*'), fmt("#6a9955")),
        ]

    def highlightBlock(self, text: str) -> None:
        """Apply every rule to one line of the document, in priority order."""
        for pattern, char_format in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), char_format)


class CodeBlock(QTextEdit):
    """
    Read-only code block.
    Height is computed purely from font metrics × line count —
    no QTimer, no parent notification needed.
    sizeHint() is also overridden so Qt layout honours it correctly.
    """
    H_LINE_EXTRA = 4    # leading between lines
    V_PAD = 32   # top+bottom padding inside the box

    def __init__(self, code: str, parent=None, highlight: bool = True):
        """Set up this widget's state and build its child widgets."""
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

        # Python code gets syntax highlighting; plain "output" blocks
        # (program output text, not code) are left as plain white text.
        if highlight:
            self._highlighter = PythonSyntaxHighlighter(self.document())

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
        """Position copy button."""
        margin = 6
        self._copy_btn.move(
            max(self.width() - self._copy_btn.width() - margin, margin), margin
        )

    def resizeEvent(self, event):
        """ResizeEvent."""
        super().resizeEvent(event)
        self._position_copy_button()

    def _copy_code(self):
        """Copy code."""
        QGuiApplication.clipboard().setText(self.toPlainText())
        self._copy_btn.setText("✓ Copied")
        QTimer.singleShot(1200, lambda: self._copy_btn.setText("📋 Copy"))

    def _calc_height(self, code: str) -> int:
        """Calc height."""
        fm = QFontMetrics(self._font)
        line_h = fm.height() + self.H_LINE_EXTRA
        lines = code.split("\n")
        n = max(len(lines), 1)
        h = line_h * n + self.V_PAD
        return max(min(h, 640), 40)

    def sizeHint(self) -> QSize:
        """SizeHint."""
        return QSize(self.width(), self._target_h)

    def minimumSizeHint(self) -> QSize:
        """MinimumSizeHint."""
        return QSize(200, self._target_h)


class MessageBubble(QWidget):
    """One chat message: renders plain text and fenced ```code``` blocks, with a typing-dots state for pending AI replies."""
    def __init__(self, text: str = "", role: str = "ai",
                 is_typing: bool = False, parent=None):
        """Set up this widget's state and build its child widgets."""
        super().__init__(parent)
        self.role = role
        self._dots = None
        self._setup(text, is_typing)

    def _setup(self, text: str, is_typing: bool):
        """Setup."""
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

    _CODE_FENCE_RE = re.compile(r"```(python|output)?\n?(.*?)```", re.DOTALL)

    def _render(self, text: str, layout: QVBoxLayout):
        """Split text on ```fenced code blocks```, rendering each as a
        CodeBlock (syntax-highlighted unless tagged "output") and every
        other segment as a plain text bubble."""
        pos = 0
        for m in self._CODE_FENCE_RE.finditer(text):
            plain = self._clean(text[pos:m.start()])
            if plain:
                layout.addWidget(self._make_label(plain))

            lang = m.group(1)
            code = self._clean(m.group(2))
            if code:
                layout.addWidget(CodeBlock(code, highlight=(lang != "output")))
            pos = m.end()

        tail = self._clean(text[pos:])
        if tail:
            layout.addWidget(self._make_label(tail))

    @staticmethod
    def _clean(s: str) -> str:
        """Strip a leading BOM/zero-width char (common copy-paste artifact) and surrounding whitespace."""
        return re.sub(r'^[\uFEFF\u200B]+', '', s).strip()

    def _make_label(self, part: str) -> QLabel:
        """Build one plain-text message bubble label."""
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
        return lbl

    def stop_typing(self):
        """Stop typing."""
        if self._dots:
            self._dots.stop()
