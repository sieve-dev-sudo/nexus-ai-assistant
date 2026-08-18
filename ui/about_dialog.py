"""
ui/about_dialog.py
────────────────────
Simple modal "About" dialog: app icon, version, author, license,
and a clickable link to the GitHub repository.
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

from LessonCodePython.theme import C, F
from LessonCodePython.version import __version__
from ui.icons import python_logo_pixmap

GITHUB_URL = "https://github.com/sieve-dev-khmer/nexus-ai-assistant"


class AboutDialog(QDialog):
    """Read-only dialog showing app version, author, license, and repo link."""

    def __init__(self, parent=None):
        """Set up this widget's state and build its child widgets."""
        super().__init__(parent)
        self.setWindowTitle("About Nexus AI")
        self.setFixedSize(340, 300)
        self.setStyleSheet(f"background:{C['bg_card']}; color:{C['text_primary']};")
        self._build()

    def _build(self) -> None:
        """Lay out the icon, title, version/author/license lines, and links."""
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(10)
        root.setAlignment(Qt.AlignTop)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(python_logo_pixmap(56))
        icon_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(icon_lbl)

        title = QLabel("Nexus AI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color:{C['brand_title']}; font-size:{F['title']+4}pt; font-weight:700;"
        )
        root.addWidget(title)

        subtitle = QLabel("Python AI Assistant")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color:{C['text_secondary']}; font-size:{F['body']}pt;")
        root.addWidget(subtitle)

        root.addSpacing(8)

        for label, value in (
            ("Version", __version__),
            ("Author", "Mr. Siev E"),
            ("License", "MIT"),
        ):
            row = QHBoxLayout()
            k = QLabel(f"{label}:")
            k.setStyleSheet(f"color:{C['text_secondary']}; font-size:{F['body']}pt;")
            v = QLabel(value)
            v.setStyleSheet(f"color:{C['text_primary']}; font-size:{F['body']}pt; font-weight:600;")
            row.addWidget(k)
            row.addStretch(1)
            row.addWidget(v)
            root.addLayout(row)

        root.addStretch(1)

        link_btn = QPushButton("🔗 GitHub Repository")
        link_btn.setCursor(Qt.PointingHandCursor)
        link_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{C['accent']}; "
            f"border:1px solid {C['border']}; border-radius:6px; padding:6px 12px; "
            f"font-size:{F['body']}pt; }}"
            f"QPushButton:hover {{ background:{C['bg_hover']}; }}"
        )
        link_btn.clicked.connect(self._open_github)
        root.addWidget(link_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        root.addWidget(close_btn)

    def _open_github(self) -> None:
        """Open the project's GitHub repository in the default browser."""
        from PyQt5.QtGui import QDesktopServices
        from PyQt5.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(GITHUB_URL))
