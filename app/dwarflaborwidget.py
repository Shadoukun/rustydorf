from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QWidget, QLabel, QGridLayout, QAbstractItemView, QHeaderView

class DwarfLaborWidget(QWidget):
    def __init__(self, data: dict[list], row: int):
        super(DwarfLaborWidget, self).__init__()
        labors: dict = data[row].get('labors', {})
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.setLayout(self.gridLayout)

        self.laborTable = QtWidgets.QTableWidget(self)
        self.laborTable.setObjectName("laborTable")

        self.laborTable.verticalHeader().hide()
        self.laborTable.horizontalHeader().hide()
        self.laborTable.setRowCount(len(labors))
        self.laborTable.setColumnCount(2)

        labors = sorted(labors.items(), key=lambda item: item[1]["id"])

        for i, labor in enumerate(labors):
            self.laborTable.setItem(i, 0, QTableWidgetItem(labor[1]["name"]))
            self.laborTable.setItem(i, 1, QTableWidgetItem(str(labor[1]["enabled"])))


        self.laborTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.laborTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.laborTable.setSelectionMode(QAbstractItemView.NoSelection)

        self.gridLayout.addWidget(self.laborTable, 0, 0, 1, 1)
