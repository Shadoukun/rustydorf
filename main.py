from PyQt5 import uic
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QGridLayout

from PyQt5.QtCore import Qt
from math import ceil
import sys
import requests

class DwarfAssistant(QMainWindow):
    def __init__(self, data: list[dict]):
        super(DwarfAssistant, self).__init__()
        uic.loadUi("main.ui", self)
        self.setGeometry(100, 100, 2000, 1000)
        self.setWindowTitle("Dwarf Assistant")
        self.nameList.setRowCount(len(data))
        self.nameList.setColumnCount(1)

        for i, entry in enumerate(data):
            item = QTableWidgetItem(f"{entry.get('first_name', 'Unknown')} {entry.get('last_name', '')}")
            self.nameList.setItem(i, 0, item)
            self.nameList.itemSelectionChanged.connect(self.change_tab)

        self.create_tabs(data)

    def create_tabs(self, data: list[dict]):

        self.tabWidget.tabBar().hide()
        # Create tabs for each dwarf
        for row in range(self.nameList.rowCount()):
            tab = DwarfInfoWidget(data, row)
            # the tab widget doesn't need to have tab titles,
            # so pass an empty string
            self.tabWidget.addTab(tab, "")


    def change_tab(self):
        """Change the tab based on the selected item in the table."""

        selected_items = self.nameList.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            row = selected_item.row()
            self.tabWidget.setCurrentIndex(row)

class DwarfInfoWidget(QWidget):
    def __init__(self, data: dict[list], row: int):
        super(DwarfInfoWidget, self).__init__()
        self.ui = DwarfForm()
        self.ui.setupUi(self)
        self.populate_info_section(data, row)
        self.populate_trait_table(data, row)

    def populate_info_section(self, data: list[dict], row: int):
        self.ui.infoSection.setLayout(QGridLayout())
        self.ui.infoSection.layout().addWidget(QLabel(f"Name: {data[row].get('first_name', 'Unknown')} {data[row].get('last_name', '')}\n" +
                                                      f"Profession: {data[row].get('profession', 'Unknown')['name']}\n" +
                                                      f"Age: {data[row].get('age', 'Unknown')}\n" +
                                                      f"Sex: {data[row].get('sex', 'Unknown')}"))

        self.ui.infoSection.layout().addItem(QSpacerItem(20, 40, 0, QSizePolicy.Expanding))

        beliefs = data[row].get('beliefs', [])
        self.ui.infoSection.layout().addWidget(QLabel("Beliefs:"))
        for belief in beliefs:
            label = QLabel(belief[0]['name'])
            self.ui.infoSection.layout().addWidget(label)

        goals = data[row].get('goals', [])
        self.ui.infoSection.layout().addWidget(QLabel("Goals:"))
        for goal in goals:
            label = QLabel(goal[0]['name'])
            self.ui.infoSection.layout().addWidget(label)

        self.ui.infoSection.layout().addItem(QSpacerItem(20, 40, 0, QSizePolicy.Expanding))

    def populate_trait_table(self, data: list[dict], row: int):
            traits = data[row].get('traits', [])

            self.ui.traitTable.verticalHeader().hide()
            self.ui.traitTable.horizontalHeader().hide()
            self.ui.traitTable.setColumnCount(8)
            self.ui.traitTable.setRowCount(15)

            row = 0
            col = 0
            for trait in traits:
                name, value = trait[0]['name'], trait[1]
                self.ui.traitTable.setItem(row, col, QTableWidgetItem(name))
                self.ui.traitTable.setItem(row, col + 1, QTableWidgetItem(str(value)))
                row += 1
                # wrap
                if row >= 15:
                    row = 0
                    col += 2

            self.ui.traitTable.resizeColumnsToContents()
            self.ui.traitTable.resizeRowsToContents()

class DwarfForm(object):
    def setupUi(self, Form):
        Form.setObjectName("DwarfForm")
        Form.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.traitTable = QtWidgets.QTableWidget(Form)

        self.infoSection = QtWidgets.QWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.infoSection.setSizePolicy(sizePolicy)
        self.infoSection.setObjectName("infoSection")
        self.gridLayout.addWidget(self.infoSection, 0, 0, 2, 2)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHeightForWidth(self.traitTable.sizePolicy().hasHeightForWidth())
        self.traitTable.setSizePolicy(sizePolicy)
        self.traitTable.setObjectName("traitTable")
        self.traitTable.setColumnCount(0)
        self.traitTable.setRowCount(0)
        self.gridLayout.addWidget(self.traitTable, 0, 1, 2, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))


if __name__ == '__main__':
    response = requests.get('http://127.0.0.1:3000/dwarves')
    data = response.json()
    app = QApplication(sys.argv)

    window = DwarfAssistant(data)
    window.show()
    sys.exit(app.exec_())