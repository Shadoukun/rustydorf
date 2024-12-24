from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker


class SignalsManager(QObject):
    sort_changed   = pyqtSignal(str, bool)

    _instance = None
    _mutex = QMutex()

    def __init__(self):
        super().__init__()

    @classmethod
    def instance(cls):
        # Thread-safe singleton initialization
        with QMutexLocker(cls._mutex):
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
