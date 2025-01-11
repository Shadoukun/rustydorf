import sys
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

STYLESHEET = '''
QProgressBar {
    background-color: transparent;
    border: 0px;
    padding: 0px;
    height: 20px;
}

QProgressBar::chunk {
    background: #CD7F32;
    width: 5px;
}
'''

class ProgressTableCell(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()
        self.setLayout(layout)

        labelWidget = QWidget(self)
        labelLayout = QHBoxLayout(labelWidget)
        labelWidget.setLayout(labelLayout)
        labelLayout.setContentsMargins(0, 0, 0, 0)

        self.nameLabel = QLabel(self)
        self.nameLabel.setText("Name")
        labelLayout.addWidget(self.nameLabel)

        labelLayout.addStretch()

        self.valueLabel = QLabel(self)
        self.valueLabel.setText("0%")
        labelLayout.addWidget(self.valueLabel)

        layout.addWidget(labelWidget, 0, 0)

        self.progress = QProgressBar()
        self.progress.setOrientation(Qt.Orientation.Horizontal)

        self.progress_value = 60
        self.progress.setStyleSheet(STYLESHEET)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(self.progress_value)
        layout.addWidget(self.progress, 0, 0)
        labelWidget.raise_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgressTableCell()
    window.show()
    sys.exit(app.exec())