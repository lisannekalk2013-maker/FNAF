"""Emergency exit: only query Escape; never intercept or suppress keyboard input."""
import ctypes
import sys
import time
from PySide6.QtCore import QObject, QEvent, Qt, QTimer
from .core import HoldToQuit


class EscapeExit(QObject):
    def __init__(self, app, quit_callback, key_reader=None):
        super().__init__(app)
        self.app = app
        self.quit_callback = quit_callback
        self.hold = HoldToQuit(5.0)
        self.local_pressed = False
        self.key_reader = key_reader
        if self.key_reader is None and sys.platform == 'win32':
            query = ctypes.windll.user32.GetAsyncKeyState
            query.argtypes = [ctypes.c_int]
            query.restype = ctypes.c_short
            self.key_reader = lambda: bool(query(0x1B) & 0x8000)
        self.app.installEventFilter(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(33)

    def eventFilter(self, watched, event):
        kind = event.type()
        if kind in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease) and event.key() == Qt.Key.Key_Escape:
            if not event.isAutoRepeat():
                self.local_pressed = kind == QEvent.Type.KeyPress
            # Let Escape retain its ordinary effect in the focused application.
        elif kind == QEvent.Type.ApplicationDeactivate:
            self.local_pressed = False
        return False

    def poll(self, now=None):
        pressed = self.key_reader() if self.key_reader else self.local_pressed
        if self.hold.update(pressed, time.monotonic() if now is None else now):
            self.timer.stop()
            self.quit_callback()

    def close(self):
        self.timer.stop()
        self.app.removeEventFilter(self)
