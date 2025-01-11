from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker


class SignalsManager(QObject):
    """
    A singleton class that manages signals used in the application.
    """

    sort_changed   = pyqtSignal(str, bool)
    populate_table = pyqtSignal(list)
    refresh_ui     = pyqtSignal()

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
