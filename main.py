from PyQt6.QtWidgets import QApplication
from PyQt6 import QtCore, QtWidgets

import sys
import requests
from pprint import pprint

from app.mainwindow import DwarfAssistant

if __name__ == '__main__':
    response = requests.get('http://127.0.0.1:3000/dwarves')
    data = response.json()
    app = QApplication(sys.argv)

    window = DwarfAssistant(data)
    window.show()
    sys.exit(app.exec())