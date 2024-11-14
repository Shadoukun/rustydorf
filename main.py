from PyQt5 import uic
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy, QGridLayout, QAbstractItemView

from PyQt5.QtCore import Qt
from math import ceil
import sys
import requests

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class DwarfAssistant(QMainWindow):
    def __init__(self, data: list[dict]):
        super(DwarfAssistant, self).__init__()
        uic.loadUi("main.ui", self)
        self.setGeometry(100, 100, 600, 300)
        self.setWindowTitle("Dwarf Assistant")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # self.menubar = QtWidgets.QMenuBar(self)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 750, 20))
        # self.menubar.setObjectName("menubar")
        # self.menuFile = QtWidgets.QMenu(self.menubar)
        # self.menuFile.setObjectName("menuFile")
        # self.setMenuBar(self.menubar)
        # self.menubar.addAction(self.menuFile.menuAction())

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.create_name_list(data)
        self.create_info_tabs(data)

        # errors if infoTabWidget is empty so do this after creating the tabs
        self.nameList.setCurrentCell(0, 0)


    def create_name_list(self, data: list[dict]):
        self.nameList = QtWidgets.QTableWidget(self.centralwidget)
        self.nameList.setObjectName("nameList")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        self.nameList.setSizePolicy(sizePolicy)
        self.nameList.setShowGrid(False)

        font = self.nameList.font()
        font.setPointSize(6)  # Set the desired font size
        self.nameList.setFont(font)
        self.nameList.setColumnCount(1)
        self.nameList.setRowCount(0)
        self.nameList.setMaximumSize(100, 16777215)
        self.nameList.horizontalHeader().setVisible(False)
        self.nameList.horizontalHeader().setHighlightSections(False)
        self.nameList.verticalHeader().setVisible(False)
        self.nameList.verticalHeader().setHighlightSections(False)

        self.gridLayout.addWidget(self.nameList, 0, 0, 1, 1)

        self.nameList.setRowCount(len(data))
        self.nameList.setColumnCount(1)

        for i, entry in enumerate(data):
            item = QTableWidgetItem(f"{entry.get('first_name', 'Unknown')} {entry.get('last_name', '')}")
            self.nameList.setItem(i, 0, item)
            self.nameList.itemSelectionChanged.connect(self.change_tab)

        self.nameList.setStyleSheet("QTableView::item:selected { border: 3px solid gold; margin-right: 2px; background-color: transparent; color: black; }")
        self.nameList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.nameList.setSelectionMode(QAbstractItemView.SingleSelection)



    def create_info_tabs(self, data: list[dict]):
        self.infoTabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.gridLayout.addWidget(self.infoTabWidget, 0, 1, 1, 1)

        self.infoTabWidget.tabBar().hide()
        # Create tabs for each dwarf
        for row in range(self.nameList.rowCount()):
            # the tab widget doesn't need to have tab titles,
            # so pass an empty string
            self.infoTabWidget.addTab(DwarfInfoWidget(data, row), "")


    def change_tab(self):
        """Change the tab based on the selected item in the table."""

        selected_items = self.nameList.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            row = selected_item.row()
            self.infoTabWidget.setCurrentIndex(row)

class DwarfInfoWidget(QWidget):

    def __init__(self, data: dict[list], row: int):
        super(DwarfInfoWidget, self).__init__()
        self.ui = DwarfForm()
        self.ui.setupUi(self)
        self.create_info_section(data, row)
        self.create_trait_table(data, row)
        self.create_thoughts_table(data, row)

    def create_info_section(self, data: list[dict], row: int):
        self.ui.infoSection.setLayout(QGridLayout())
        self.ui.infoSection.layout().addWidget(QLabel(f"Name: {data[row].get('first_name', 'Unknown')} {data[row].get('last_name', '')}\n" +
                                                      f"Profession: {data[row].get('profession', 'Unknown')['name']}\n" +
                                                      f"Age: {data[row].get('age', 'Unknown')}\n" +
                                                      f"Sex: {data[row].get('sex', 'Unknown')}"))

        font = self.ui.infoSection.font()
        font.setPointSize(6)  # Set the desired font size
        self.ui.infoSection.setFont(font)

        belief_string = "Beliefs: \n"
        beliefs = data[row].get('beliefs', [])
        # create rows
        belief_list = [beliefs[i:i+4] for i in range(0, len(beliefs), 4)]
        belief_list = [[belief[0]['name'] for belief in belief_group] for belief_group in belief_list]
        for b in belief_list:
            belief_string += f" {', '.join(b)}\n"
        self.ui.infoSection.layout().addWidget(QLabel(belief_string))

        goal_string = "Goals: \n"
        for goal in data[row].get('goals', []):
            goal_string += f" {goal[0]['name']}\n"
        self.ui.infoSection.layout().addWidget(QLabel(goal_string))
        self.ui.infoSection.layout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def create_trait_table(self, data: list[dict], row: int):
        traits = data[row].get('traits', [])

        self.ui.traitTable.verticalHeader().hide()
        self.ui.traitTable.horizontalHeader().hide()
        self.ui.traitTable.setColumnCount(2)
        self.ui.traitTable.setRowCount(len(traits))

        row = 0
        for trait in traits:
            name, value = trait[0]['name'], trait[1]
            self.ui.traitTable.setItem(row, 0, QTableWidgetItem(name))
            self.ui.traitTable.setItem(row, 1, QTableWidgetItem(str(value)))
            row += 1

        # shrink the table to fit the contents
        self.ui.traitTable.resizeColumnsToContents()
        self.ui.traitTable.resizeRowsToContents()
        self.ui.traitTable.setFixedWidth(self.ui.traitTable.columnWidth(0))

        font = self.ui.traitTable.font()
        font.setPointSize(6)  # Set the desired font size
        self.ui.traitTable.setFont(font)
        self.ui.traitTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.ui.traitTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def create_thoughts_table(self, data: list[dict], row: int):
        thoughts = data[row].get('thoughts', [])

        thoughtsTable = QTableWidget()
        thoughtsTable.verticalHeader().hide()
        thoughtsTable.horizontalHeader().hide()
        thoughtsTable.setColumnCount(1)
        thoughtsTable.setRowCount(len(thoughts))

        row = 0
        for thought in thoughts:
            text = f"felt {thought['emotion_type'].lower()} {thought['thought']}"
            thoughtsTable.setItem(row, 0, QTableWidgetItem(text))
            row += 1

        thoughtsTable.resizeColumnsToContents()
        thoughtsTable.resizeRowsToContents()
        self.ui.infoSection.layout().addWidget(thoughtsTable)


class DwarfForm(object):
    def setupUi(self, Form):
        Form.setObjectName("DwarfForm")
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.traitTable = QtWidgets.QTableWidget(Form)

        self.infoSection = QtWidgets.QWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.infoSection.setSizePolicy(sizePolicy)
        self.infoSection.setObjectName("infoSection")
        self.gridLayout.addWidget(self.infoSection, 0, 0, 1, 1)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.traitTable.setSizePolicy(sizePolicy)
        self.traitTable.setObjectName("traitTable")
        self.gridLayout.addWidget(self.traitTable, 0, 1, 1, 1)

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