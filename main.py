from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtWidgets

import sys
import requests
from pprint import pprint

from app.mainwindow import DwarfAssistant

# Enable high DPI scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

if __name__ == '__main__':
    response = requests.get('http://127.0.0.1:3000/dwarves')
    data = response.json()
    app = QApplication(sys.argv)

    window = DwarfAssistant(data)
    window.show()
    sys.exit(app.exec_())