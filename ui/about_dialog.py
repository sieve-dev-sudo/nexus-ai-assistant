"""
ui/about_dialog.py
────────────────────
Simple modal "About" dialog: app icon, version, author, license,
and a clickable link to the GitHub repository.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

from LessonCodePython.theme import C, F
from LessonCodePython.version import __version__
from ui.icons import python_logo_pixmap

GITHUB_URL = "https://github.com/sieve-dev-sudo/nexus-ai-assistant"


class AboutDialog(QDialog):
    """Read-only dialog showing app version, author, license, and repo link."""

    def __init__(self, parent=None):
        """Set up this widget's state and build its child widgets."""
        super().__init__(parent)
        self.setWindowTitle("About Nexus AI")
        # Drop the title-bar "?" context-help button (Windows adds it by
        # default to QDialog; it does nothing useful here).
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedWidth(360)
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
        root.setContentsMargins(28, 28, 28, 22)
        root.setSpacing(4)
        root.setAlignment(Qt.AlignTop)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(python_logo_pixmap(64))
        icon_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(icon_lbl)

        root.addSpacing(10)

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

        root.addSpacing(18)

        # ── Info card ──
        card = QFrame()
        card.setObjectName("infoCard")
        card.setStyleSheet(
            f"QFrame#infoCard {{ background:{C['bg_card']}; "
            f"border:1px solid {C['border']}; border-radius:10px; }}"
        )
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(18, 16, 18, 16)
        card_lay.setSpacing(14)

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
            k.setMinimumHeight(F['body'] + 12)
            v = QLabel(value)
            v.setStyleSheet(
                f"color:{C['text_primary']}; font-size:{F['body']}pt; "
                f"font-weight:600; background:transparent;"
            )
            v.setMinimumHeight(F['body'] + 12)
            row.addWidget(k)
            row.addStretch(1)
            row.addWidget(v)
            card_lay.addLayout(row)

        root.addWidget(card)
        root.addSpacing(16)

        # GitHub link — a rich-text hyperlink label reads more cleanly
        # than a button here, and sidesteps emoji/button rendering
        # inconsistencies across platforms.
        link_lbl = QLabel(f'<a href="{GITHUB_URL}" style="color:{C["accent"]}; '
                           f'text-decoration:none;">🔗 GitHub Repository</a>')
        link_lbl.setAlignment(Qt.AlignCenter)
        link_lbl.setOpenExternalLinks(True)
        link_lbl.setCursor(Qt.PointingHandCursor)
        link_lbl.setStyleSheet(f"font-size:{F['body']}pt; background:transparent;")
        root.addWidget(link_lbl)

        root.addStretch(1)

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

    def _open_github(self) -> None:
        """Open the project's GitHub repository in the default browser."""
        QDesktopServices.openUrl(QUrl(GITHUB_URL))
