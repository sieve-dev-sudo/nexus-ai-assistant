"""
ui/about_dialog.py
────────────────────
Simple modal "About" dialog: app icon, version, author, and license.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt5.QtCore import Qt

from LessonCodePython.theme import C, F
from LessonCodePython.version import __version__
from ui.icons import python_logo_pixmap


class AboutDialog(QDialog):
    """Read-only dialog showing app version, author, and license."""

    def __init__(self, parent=None):
        """Set up this widget's state and build its child widgets."""
        super().__init__(parent)
        self.setWindowTitle("About Nexus AI")
        # Drop the title-bar "?" context-help button (Windows adds it by
        # default to QDialog; it does nothing useful here).
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedWidth(380)
        self.setStyleSheet(f"background:{C['bg_main']}; color:{C['text_primary']};")
        self._build()
        # Let the dialog's height follow its content's natural size
        # instead of a hand-guessed pixel value — font metrics differ
        # enough across OSes that a fixed height clips/overlaps content.
        self.adjustSize()
        self.setFixedHeight(self.sizeHint().height())

    def _build(self) -> None:
        """Lay out the icon, title, an info card, and the footer links."""
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 22)
        root.setSpacing(4)
        root.setAlignment(Qt.AlignTop)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(python_logo_pixmap(48))
        icon_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(icon_lbl)

        root.addSpacing(6)

        title = QLabel("Nexus AI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color:{C['brand_title']}; font-size:{F['title']+6}pt; font-weight:700; "
            f"background:transparent;"
        )
        root.addWidget(title)

        subtitle = QLabel("Python AI Assistant")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"color:{C['text_secondary']}; font-size:{F['body']}pt; background:transparent;"
        )
        root.addWidget(subtitle)

        root.addSpacing(12)

        # ── Info card ──
        card = QFrame()
        card.setObjectName("infoCard")
        card.setStyleSheet(
            f"QFrame#infoCard {{ background:{C['bg_card']}; "
            f"border:1px solid {C['border']}; border-radius:10px; }}"
        )
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(18, 10, 18, 10)
        card_lay.setSpacing(8)

        for label, value in (
            ("Version", __version__),
            ("Author", "Mr. Siev E"),
            ("License", "MIT"),
        ):
            row = QHBoxLayout()
            row.setSpacing(8)
            k = QLabel(label)
            k.setStyleSheet(
                f"color:{C['text_secondary']}; font-size:{F['body']}pt; background:transparent;"
            )
            k.setMinimumHeight(F['body'] + 6)
            v = QLabel(value)
            v.setStyleSheet(
                f"color:{C['text_primary']}; font-size:{F['body']}pt; "
                f"font-weight:600; background:transparent;"
            )
            v.setMinimumHeight(F['body'] + 6)
            row.addWidget(k)
            row.addStretch(1)
            row.addWidget(v)
            card_lay.addLayout(row)

        root.addWidget(card)
        root.addSpacing(16)

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(
            f"QPushButton {{ background:{C['accent']}; color:white; "
            f"border:none; border-radius:8px; padding:9px 0; "
            f"font-size:{F['body']}pt; font-weight:600; }}"
            f"QPushButton:hover {{ background:{C['accent2']}; }}"
        )
        close_btn.clicked.connect(self.accept)
        root.addWidget(close_btn)
