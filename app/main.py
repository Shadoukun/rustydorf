import sys
from PyQt6.QtWidgets import QApplication

from app.dwarfassistant.mainwindow import DwarfAssistant

def main():
    app = QApplication(sys.argv)
    window = DwarfAssistant()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
