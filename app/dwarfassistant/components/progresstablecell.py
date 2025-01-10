import sys
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

class ProgressTableCell(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()
        self.setLayout(layout)

        labelWidget = QWidget(self)
        labelLayout = QHBoxLayout(labelWidget)
        labelWidget.setLayout(labelLayout)
        labelLayout.setContentsMargins(0, 0, 0, 0)

        self.leftLabel = QLabel(self)
        self.leftLabel.setText("Name")
        labelLayout.addWidget(self.leftLabel)

        labelLayout.addStretch()

        self.rightLabel = QLabel(self)
        self.rightLabel.setText("0%")
        labelLayout.addWidget(self.rightLabel)

        layout.addWidget(labelWidget, 0, 0)

        progress = QProgressBar()
        progress.setOrientation(Qt.Orientation.Horizontal)

        self.progress_color = "red"
        self.progress_value = 60
        stylesheet = '''
        QProgressBar {
            background-color: transparent;
            border: 0px;
            padding: 0px;
            height: 20px;
        }

        QProgressBar::chunk {''' + \
            f"background: {self.progress_color};" + '''
            width: 5px
        }
        '''
        progress.setStyleSheet(stylesheet)
        progress.setTextVisible(False)
        progress.setRange(0, 100)
        progress.setValue(self.progress_value)
        layout.addWidget(progress, 0, 0)
        labelWidget.raise_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgressTableCell()
    window.show()
    sys.exit(app.exec())