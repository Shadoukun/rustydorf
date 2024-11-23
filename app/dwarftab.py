from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QWidget, QLabel, QGridLayout, QAbstractItemView, QHeaderView, QBoxLayout
from app.dwarfinfowidget import DwarfInfoWidget
from app.dwarflaborwidget import DwarfLaborWidget

class DwarfTabWidget(QWidget):
    def __init__(self, data: dict[list], row: int):
        super(DwarfTabWidget, self).__init__()

        self.layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.setLayout(self.layout)
        self.centralwidget = QtWidgets.QTabWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.infotab = DwarfInfoWidget(data, row)
        self.centralwidget.addTab(self.infotab, "Info")
        self.centralwidget.addTab(DwarfLaborWidget(data, row), "Labor")
        self.layout.addWidget(self.centralwidget)
