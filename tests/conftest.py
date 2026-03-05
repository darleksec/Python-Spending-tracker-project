"""conftest.py — Mock PyQt6 if not installed so pure-logic tests can run."""

import sys
from unittest.mock import MagicMock

# If PyQt6 is not installed, provide a minimal mock so that modules importing
# PyQt6.QtCore / PyQt6.QtWidgets can be loaded for unit-testing pure logic.
if "PyQt6" not in sys.modules:
    pyqt6 = MagicMock()

    # QObject base class — needs to be a real class so ThemeManager can subclass it
    class _QObject:
        def __init__(self, *a, **kw):
            pass

    # pyqtSignal — return a dummy descriptor
    class _pyqtSignal:
        def __init__(self, *args, **kwargs):
            pass
        def emit(self, *args):
            pass
        def connect(self, *args):
            pass
        def __set_name__(self, owner, name):
            pass
        def __get__(self, obj, objtype=None):
            return self

    pyqt6_qtcore = MagicMock()
    pyqt6_qtcore.QObject = _QObject
    pyqt6_qtcore.pyqtSignal = _pyqtSignal

    sys.modules["PyQt6"] = pyqt6
    sys.modules["PyQt6.QtCore"] = pyqt6_qtcore
    sys.modules["PyQt6.QtWidgets"] = MagicMock()
    sys.modules["PyQt6.QtGui"] = MagicMock()
