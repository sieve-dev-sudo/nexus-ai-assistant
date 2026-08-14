"""
ui/avatars.py — Avatar label + animated typing dots.
"""

from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

from LessonCodePython.theme import C


class AvatarLabel(QLabel):
    """Small circular badge showing an emoji/initial for a chat message's sender."""
    def __init__(self, text: str, bg: str, size: int = 38, parent=None):
        """Set up this widget's state and build its child widgets."""
        super().__init__(text, parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f"background:{bg}; border-radius:{size // 2}px; "
            f"color:#fff; font-size:{size // 2 - 1}px; font-weight:600;"
        )


class TypingDots(QWidget):
    """Animated three-dot "typing…" indicator shown while waiting for a response."""
    DOT_COLORS = [C["dot_1"], C["dot_2"], C["dot_3"]]
    DOT_SIZE = 9

    def __init__(self, parent=None):
        """Set up this widget's state and build its child widgets."""
        super().__init__(parent)
        self._offsets = [0, 0, 0]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._step = 0
        self.setFixedHeight(28)
        self.setMinimumWidth(54)

    def start(self):
        """Start the animation timer."""
        self._timer.start(120)

    def stop(self):
        """Stop the animation timer."""
        self._timer.stop()

    def _tick(self):
        """Tick."""
        self._step = (self._step + 1) % 9
        for i in range(3):
            phase = (self._step - i * 2) % 9
            self._offsets[i] = -5 if phase in (0, 1) else 0
        self.update()

    def paintEvent(self, _):
        """PaintEvent."""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        x = 6
        for i, color in enumerate(self.DOT_COLORS):
            p.setBrush(QColor(color))
            p.setPen(Qt.NoPen)
            y = (self.height() - self.DOT_SIZE) // 2 + self._offsets[i]
            p.drawEllipse(x, y, self.DOT_SIZE, self.DOT_SIZE)
            x += self.DOT_SIZE + 7
        p.end()
