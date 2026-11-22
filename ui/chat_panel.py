"""
ui/chat_panel.py
──────────────────
Scrollable message list + input bar for one mode (Lesson or Fix Code).
Each panel has its own engine instance and independent chat history.
Engine runs in a background QThread so the UI never freezes.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QPushButton,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer

from LessonCodePython.theme import C, F
from ui.message_bubble import MessageBubble
from ui.input_bar import InputBar


class _Worker(QObject):
    """Runs the (possibly slow) engine.get_response() call off the UI thread."""
    finished = pyqtSignal(str)

    def __init__(self, engine, text: str):
        """Set up this widget's state and build its child widgets."""
        super().__init__()
        self._engine = engine
        self._text = text

    def run(self):
        """Run the engine. Always emits finished, even if the engine
        raises, so the input box is never left disabled forever."""
        try:
            reply = self._engine.get_response(self._text)
        except Exception as exc:  # never leave the UI stuck
            reply = f"⚠️ មានបញ្ហាខាងក្នុង: {type(exc).__name__}: {exc}"
        self.finished.emit(reply)


class ChatPanel(QWidget):
    """Scrollable message list + input bar for one engine (Lesson or Fix Code), including its own chat history (used by Clear Chat's Undo)."""
    def __init__(self, engine, welcome_text: str = "", parent=None):
        """Set up this widget's state and build its child widgets."""
        super().__init__(parent)
        self._engine = engine
        self._typing_bubble = None
        self._thread = None
        self._worker = None
        self._history = []  # list of (role, text), kept so Clear Chat can Undo
        self._welcome_text = welcome_text
        self._undo_snapshot = None   # history saved by clear_chat(), for Undo
        self._undo_banner = None
        self._undo_timer = None
        self._ignore_next_reply = False  # set by clear_chat() while busy
        self._build()
        if welcome_text:
            self._add_ai_bubble(welcome_text)

    # ── build ────────────────────────────────────────────────────────────
    def _build(self):
        """Build."""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ background:{C['bg_main']}; border:none; }}"
            f"QScrollBar:vertical {{ background:{C['bg_card']}; width:6px; border:none; }}"
            f"QScrollBar::handle:vertical {{ background:{C['border']}; border-radius:3px; }}"
        )

        self._container = QWidget()
        self._container.setStyleSheet(f"background:{C['bg_main']};")
        self._msg_lay = QVBoxLayout(self._container)
        self._msg_lay.setContentsMargins(16, 16, 16, 16)
        self._msg_lay.setSpacing(4)
        self._msg_lay.addStretch()   # pushes messages to top

        self._scroll.setWidget(self._container)

        # Input bar
        self._bar = InputBar()
        self._bar.submitted.connect(self._on_send)

        lay.addWidget(self._scroll)
        lay.addWidget(self._bar)

    # ── public ───────────────────────────────────────────────────────────
    def set_placeholder(self, text: str):
        """Set placeholder."""
        self._bar.set_placeholder(text)

    def focus_input(self):
        """Focus input."""
        self._bar.focus()

    def clear_input(self):
        """Clear input."""
        self._bar.clear_input()

    def inject_text(self, text: str):
        """Pre-fill + auto-send (used by sidebar topic shortcuts)."""
        self._on_send(text)

    def clear_chat(self):
        """Remove every message bubble and reset history, then show the
        welcome message again (if this panel has one) — same state as
        a fresh app launch. Keeps a snapshot for 10 seconds so the user
        can Undo before it's gone for good."""
        self._undo_snapshot = list(self._history)  # copy, for potential undo

        # A reply still being computed belongs to the old conversation:
        # drop it when it arrives instead of adding it to the new chat.
        if self.is_busy():
            self._ignore_next_reply = True
        self._typing_bubble = None  # its widget is deleted just below

        while self._msg_lay.count() > 1:  # keep the trailing stretch
            item = self._msg_lay.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.deleteLater()
        self._history = []
        if self._welcome_text:
            self._add_ai_bubble(self._welcome_text)

        self._show_undo_banner()

    def _show_undo_banner(self):
        """Show a dismissible "Chat cleared — Undo" bar for 10 seconds."""
        self._remove_banner_widgets()  # clear any stale banner UI only —
        # NOT _dismiss_undo_banner(), which would also wipe the snapshot
        # we just captured in clear_chat().

        banner = QWidget()
        banner.setStyleSheet(f"background:{C['bg_card']}; border-bottom:1px solid {C['border']};")
        row = QHBoxLayout(banner)
        row.setContentsMargins(16, 8, 16, 8)

        label = QLabel("Chat cleared")
        label.setStyleSheet(f"color:{C['text_secondary']}; font-size:{F['label']}pt;")
        row.addWidget(label)
        row.addStretch(1)

        undo_btn = QPushButton("Undo")
        undo_btn.setCursor(Qt.PointingHandCursor)
        undo_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{C['accent']}; "
            f"border:none; font-weight:600; font-size:{F['label']}pt; }}"
            f"QPushButton:hover {{ text-decoration:underline; }}"
        )
        undo_btn.clicked.connect(self._undo_clear)
        row.addWidget(undo_btn)

        self.layout().insertWidget(0, banner)
        self._undo_banner = banner

        self._undo_timer = QTimer(self)
        self._undo_timer.setSingleShot(True)
        self._undo_timer.timeout.connect(self._dismiss_undo_banner)
        self._undo_timer.start(10_000)

    def _remove_banner_widgets(self):
        """Tear down the banner + timer only — never touches the undo
        snapshot itself (see _show_undo_banner / _dismiss_undo_banner)."""
        if self._undo_timer is not None:
            self._undo_timer.stop()
            self._undo_timer = None
        if self._undo_banner is not None:
            self._undo_banner.deleteLater()
            self._undo_banner = None

    def _dismiss_undo_banner(self):
        """Called when the 10s window truly expires with no Undo click:
        hide the banner AND permanently discard the snapshot."""
        self._remove_banner_widgets()
        self._undo_snapshot = None

    def _undo_clear(self):
        """Restore the chat exactly as it was before the last Clear Chat."""
        if self._undo_snapshot is None:
            return
        snapshot = self._undo_snapshot

        while self._msg_lay.count() > 1:
            item = self._msg_lay.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.deleteLater()
        self._history = []

        for role, text in snapshot:
            if role == "user":
                self._add_user_bubble(text)
            else:
                self._add_ai_bubble(text)

        self._remove_banner_widgets()
        self._undo_snapshot = None

    def is_busy(self) -> bool:
        """True while a reply is still being computed in the background."""
        # Cleared only by _on_thread_done(), i.e. after the QThread has
        # fully stopped, not just after the reply arrived.
        return self._thread is not None

    # ── private ──────────────────────────────────────────────────────────
    def _on_send(self, text: str):
        """Send one message to the engine on a background thread.

        Ignored while a previous reply is still running: the sidebar
        topic buttons stay clickable, and starting a second QThread
        used to replace the running one and crash the app with
        "QThread: Destroyed while thread is still running"."""
        if self.is_busy():
            return

        self._add_user_bubble(text)
        self._bar.set_enabled(False)
        self._show_typing()

        self._thread = QThread()
        self._worker = _Worker(self._engine, text)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_response)
        self._worker.finished.connect(self._thread.quit)
        # Free the worker and thread once the thread has really stopped.
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        thread = self._thread
        thread.finished.connect(lambda: self._on_thread_done(thread))
        thread.start()

    def _on_thread_done(self, thread: QThread):
        """Forget the finished thread so is_busy() returns False."""
        if self._thread is thread:
            self._thread = None
            self._worker = None

    def _on_response(self, text: str):
        """Show the engine's reply (unless the chat was cleared meanwhile)."""
        self._remove_typing()
        if self._ignore_next_reply:
            self._ignore_next_reply = False
        else:
            self._add_ai_bubble(text)
        self._bar.set_enabled(True)
        self._bar.focus()

    def _add_user_bubble(self, text: str):
        """Add user bubble."""
        b = MessageBubble(text, role="user")
        self._msg_lay.insertWidget(self._msg_lay.count() - 1, b)
        self._history.append(("user", text))
        self._bottom()

    def _add_ai_bubble(self, text: str):
        """Add ai bubble."""
        b = MessageBubble(text, role="ai")
        self._msg_lay.insertWidget(self._msg_lay.count() - 1, b)
        self._history.append(("ai", text))
        self._bottom()

    def _show_typing(self):
        """Show typing."""
        self._typing_bubble = MessageBubble(role="ai", is_typing=True)
        self._msg_lay.insertWidget(self._msg_lay.count() - 1, self._typing_bubble)
        self._bottom()

    def _remove_typing(self):
        """Remove typing."""
        if self._typing_bubble:
            self._typing_bubble.stop_typing()
            self._msg_lay.removeWidget(self._typing_bubble)
            self._typing_bubble.deleteLater()
            self._typing_bubble = None

    def _bottom(self):
        """Bottom."""
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.maximum())
