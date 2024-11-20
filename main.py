from PyQt5 import uic
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QWidget, QLabel, QGridLayout, QAbstractItemView
from PyQt5.QtGui import QFont
import sys
import requests

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class DwarfAssistant(QMainWindow):

    def __init__(self, data: list[dict]):
        super(DwarfAssistant, self).__init__()
        self.setWindowTitle("Dwarf Assistant")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        # Set font on central widget
        font = QFont()
        font.setPointSize(6)
        self.setFont(font)
        self._menu_bar()
        self._name_list(data)
        self._main_panel(data)

        # this errors if infoTabWidget is empty so do this after creating the tabs
        self.nameList.setCurrentCell(0, 0)

    def _menu_bar(self):
        # Create empty menu bar and status bar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    def _name_list(self, data: list[dict]):
        '''Create the table of names on the left side of the window.'''

        self.nameList = QtWidgets.QTableWidget(self.centralwidget)
        self.nameList.setObjectName("nameList")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        self.nameList.setSizePolicy(sizePolicy)
        self.nameList.setShowGrid(False)

        # for some reason the nameList font size is not
        # being set by by the central widget font
        font = self.nameList.font()
        font.setPointSize(6)
        self.nameList.setFont(font)

        self.nameList.setMaximumWidth(100)
        self.nameList.setColumnCount(1)
        self.nameList.setRowCount(len(data))
        self.nameList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.nameList.setSelectionMode(QAbstractItemView.SingleSelection)

        self.nameList.horizontalHeader().setVisible(False)
        self.nameList.horizontalHeader().setHighlightSections(False)
        self.nameList.verticalHeader().setVisible(False)
        self.nameList.verticalHeader().setHighlightSections(False)

        for i, entry in enumerate(data):
            item = QTableWidgetItem(f"{entry.get('first_name', 'Unknown')} {entry.get('last_name', '')}")
            self.nameList.setItem(i, 0, item)
            self.nameList.itemSelectionChanged.connect(self.change_tab)

        self.nameList.setStyleSheet(
            """QTableView::item:selected { \
                border: 3px solid gold; \
                margin-right: 2px; \
                background-color: transparent; \
                color: black; \
            }""")

        self.gridLayout.addWidget(self.nameList, 0, 0, 1, 1)

    def _main_panel(self, data: list[dict]):
        '''Create the main panel on the right side of the window.'''

        self.mainPanel = QtWidgets.QTabWidget(self.centralwidget)

        # Create tabs for each dwarf
        for row in range(self.nameList.rowCount()):
            # the tab widget doesn't need to have tab titles,
            # so pass an empty string
            self.mainPanel.addTab(DwarfInfoWidget(data, row), "")

        self.mainPanel.tabBar().hide()
        self.gridLayout.addWidget(self.mainPanel, 0, 1, 1, 1)


    def change_tab(self):
        '''Change the tab when a new name is selected in the name list.'''

        selected_items = self.nameList.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            row = selected_item.row()
            self.mainPanel.setCurrentIndex(row)


class DwarfInfoWidget(QWidget):

    def __init__(self, data: dict[list], row: int):
        super(DwarfInfoWidget, self).__init__()
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.infoSection = QtWidgets.QWidget(self)
        self.infoSection.setLayout(QGridLayout())
        self.infoSection.setObjectName("infoSection")

        self.goalsBeliefs = QtWidgets.QWidget(self)
        self.goalsBeliefs.setLayout(QGridLayout())
        self.goalsBeliefs.setObjectName("goalsBeliefs")

        self.thoughtsTable = QtWidgets.QTableWidget(self)
        self.thoughtsTable.setObjectName("thoughtsTable")

        self.attributeTable = QtWidgets.QTableWidget(self)

        self.traitTable = QtWidgets.QTableWidget(self)
        self.traitTable.setObjectName("traitTable")

        self._info_section(data, row)
        self._attribute_table(data, row)
        self._trait_table(data, row)
        self._thoughts_table(data, row)
        self._beliefs_table(data, row)
        self._goals_table(data, row)

        self.gridLayout.addWidget(self.infoSection, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.goalsBeliefs, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.thoughtsTable, 2, 0, 1, 2)
        self.gridLayout.addWidget(self.attributeTable, 0, 2, 3, 1)
        self.gridLayout.addWidget(self.traitTable, 0, 3, 3, 1)

    def _info_section(self, data: list[dict], row: int):
        info = QLabel(f"Name: {data[row].get('first_name', 'Unknown')} {data[row].get('last_name', '')}\n" +
                      f"Profession: {data[row].get('profession', 'Unknown')['name']}\n" +
                      f"Age: {data[row].get('age', 'Unknown')}\n" +
                      f"Sex: {data[row].get('sex', 'Unknown')}")
        self.infoSection.layout().addWidget(info)

    def _attribute_table(self, data: list[dict], row: int):
        attributes: dict = data[row].get('attributes', {})
        self.attributeTable.verticalHeader().hide()
        self.attributeTable.horizontalHeader().hide()
        self.attributeTable.setColumnCount(2)
        self.attributeTable.setRowCount(len(attributes))

        row = 0
        p = True
        for attribute in attributes.items():
            name, value = attribute[0], attribute[1]['value']
            self.attributeTable.setItem(row, 0, QTableWidgetItem(name))
            self.attributeTable.setItem(row, 1, QTableWidgetItem(str(value)))
            row += 1

        self.attributeTable.resizeColumnsToContents()
        self.attributeTable.resizeRowsToContents()

        self.attributeTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.attributeTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.attributeTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.attributeTable.setSelectionMode(QAbstractItemView.NoSelection)

    def _trait_table(self, data: list[dict], row: int):
        traits = data[row].get('traits', [])

        self.traitTable.verticalHeader().hide()
        self.traitTable.horizontalHeader().hide()
        self.traitTable.setColumnCount(2)
        self.traitTable.setRowCount(len(traits))

        row = 0
        for trait in traits:
            name, value = trait[0]['name'], trait[1]
            self.traitTable.setItem(row, 0, QTableWidgetItem(name))
            self.traitTable.setItem(row, 1, QTableWidgetItem(str(value)))
            row += 1

        # set the vertical header to resize to the contents
        # This feels janky but it works
        self.traitTable.resizeColumnsToContents()
        self.traitTable.resizeRowsToContents()
        self.traitTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.traitTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.traitTable.setFixedWidth(self.traitTable.columnWidth(0))

        self.traitTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.traitTable.setSelectionMode(QAbstractItemView.NoSelection)

    def _thoughts_table(self, data: list[dict], row: int):
        thoughts = data[row].get('thoughts', [])

        self.thoughtsTable.verticalHeader().hide()
        self.thoughtsTable.horizontalHeader().hide()
        self.thoughtsTable.setColumnCount(1)
        self.thoughtsTable.setRowCount(len(thoughts))

        row = 0
        for thought in thoughts:
            text = f"felt {thought['emotion_type'].lower()} {thought['thought']}"
            self.thoughtsTable.setItem(row, 0, QTableWidgetItem(text))
            row += 1

        self.thoughtsTable.resizeColumnsToContents()
        self.thoughtsTable.resizeRowsToContents()

        self.thoughtsTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.thoughtsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.thoughtsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.thoughtsTable.setSelectionMode(QAbstractItemView.NoSelection)

    def _beliefs_table(self, data: list[dict], row: int):
        beliefs = data[row].get('beliefs', [])

        beliefsTable = QTableWidget()
        beliefsTable.verticalHeader().hide()
        beliefsTable.horizontalHeader().hide()
        beliefsTable.setRowCount(len(beliefs))
        beliefsTable.setColumnCount(2)

        row = 0
        for belief in beliefs:
            name, value = belief[0]['name'], belief[1]
            beliefsTable.setItem(row, 0, QTableWidgetItem(belief[0]['name']))
            beliefsTable.setItem(row, 1, QTableWidgetItem(str(belief[1])))
            row += 1

        beliefsTable.resizeColumnsToContents()
        beliefsTable.resizeRowsToContents()

        # set the vertical header to resize to the contents and stretch the first column
        beliefsTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        beliefsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        beliefsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        beliefsTable.setSelectionMode(QAbstractItemView.NoSelection)

        self.goalsBeliefs.layout().addWidget(beliefsTable, 0, 0)

    def _goals_table(self, data: list[dict], row: int):
        goals = data[row].get('goals', [])

        goalsTable = QTableWidget()
        goalsTable.verticalHeader().hide()
        goalsTable.horizontalHeader().hide()
        goalsTable.setRowCount(len(goals))
        goalsTable.setColumnCount(2)

        row = 0
        for goal in goals:
            name, value = goal[0]['name'], goal[1]
            goalsTable.setItem(row, 0, QTableWidgetItem(goal[0]['name']))
            goalsTable.setItem(row, 1, QTableWidgetItem(str(goal[1])))
            row += 1

        goalsTable.resizeColumnsToContents()
        goalsTable.resizeRowsToContents()

        # set the vertical header to resize to the contents and stretch the first column
        goalsTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        goalsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        goalsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        goalsTable.setSelectionMode(QAbstractItemView.NoSelection)

        self.goalsBeliefs.layout().addWidget(goalsTable, 0, 1)


if __name__ == '__main__':
    response = requests.get('http://127.0.0.1:3000/dwarves')
    data = response.json()
    app = QApplication(sys.argv)

    window = DwarfAssistant(data)
    window.show()
    sys.exit(app.exec_())