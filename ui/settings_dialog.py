"""
ui/settings_dialog.py
──────────────────────
Simple modal dialog: theme (dark/light) + font size scale.
Saves to LessonCodePython/settings_manager.py's JSON file. Changes
apply on next app restart — this dialog says so plainly rather than
attempting a live re-style of every already-built widget.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSlider, QPushButton, QMessageBox,
)
from PyQt5.QtCore import Qt

from LessonCodePython.theme import C, F
from LessonCodePython.settings_manager import load_settings, save_settings


class SettingsDialog(QDialog):
    """Modal dialog for choosing the theme and font size (applies on restart)."""
    def __init__(self, parent=None):
        """Set up this widget's state and build its child widgets."""
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(360, 220)
        self.setStyleSheet(f"background:{C['bg_card']}; color:{C['text_primary']};")

        self._settings = load_settings()
        self._build()

    def _build(self):
        """Build."""
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel("⚙️  Settings")
        title.setStyleSheet(f"font-size:{F['title']}pt; font-weight:700;")
        root.addWidget(title)

        # ── Theme ──
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme:"))
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Dark", "Light"])
        self._theme_combo.setCurrentText(
            "Light" if self._settings.get("theme") == "light" else "Dark"
        )
        theme_row.addWidget(self._theme_combo, stretch=1)
        root.addLayout(theme_row)

        # ── Font size ──
        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Font size:"))
        self._font_slider = QSlider(Qt.Horizontal)
        self._font_slider.setMinimum(80)
        self._font_slider.setMaximum(150)
        self._font_slider.setValue(round(self._settings.get("font_scale", 1.0) * 100))
        font_row.addWidget(self._font_slider, stretch=1)
        self._font_value_lbl = QLabel(f"{self._font_slider.value()}%")
        self._font_slider.valueChanged.connect(
            lambda v: self._font_value_lbl.setText(f"{v}%")
        )
        font_row.addWidget(self._font_value_lbl)
        root.addLayout(font_row)

        note = QLabel("* ត្រូវ restart App ដើម្បីឲ្យការផ្លាស់ប្តូរដំណើរការ")
        note.setStyleSheet(f"color:{C['text_secondary']}; font-size:{F['label']}pt;")
        note.setWordWrap(True)
        root.addWidget(note)

        root.addStretch(1)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
            f"background:{C['accent']}; color:white; border-radius:6px; padding:6px 16px;"
        )
        save_btn.clicked.connect(self._on_save)
        btn_row.addStretch(1)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

    def _on_save(self):
        """On save."""
        new_settings = {
            "theme": "light" if self._theme_combo.currentText() == "Light" else "dark",
            "font_scale": self._font_slider.value() / 100,
        }
        ok = save_settings(new_settings)
        if ok:
            QMessageBox.information(
                self, "Settings",
                "បានរក្សាទុក! សូម restart App ដើម្បីឲ្យការផ្លាស់ប្តូរដំណើរការ។"
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Settings", "រក្សាទុកមិនជោគជ័យទេ — សូមសាកល្បងម្តងទៀត។")
