from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QSizePolicy, QWidget, QVBoxLayout, QLineEdit, QComboBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

from .dropdowncombobox import DropdownComboBox

class NameListWidget(QWidget):

    def __init__(self, parent=None, game_data: dict = None, dwarves: list[dict] = None):
        super().__init__(parent)
        self.setObjectName("nameList")
        self.game_data = game_data
        self.dwarves = dwarves
        self.order = []

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setSizePolicy(sizePolicy)
        self.setMaximumWidth(150)

        self.searchBar = DropdownComboBox(self)
        self.searchBar.setObjectName("nameListSearchBar")
        self.searchBar.setPlaceholderText("Search")
        self.populate_search_bar()
        layout.addWidget(self.searchBar)

        self.nameTable = NameListTable(self, self.game_data, self.dwarves)
        self.nameTable.setObjectName("nameTable")
        layout.addWidget(self.nameTable)

    def populate_search_bar(self):
        # TODO: finish this.
        # I need to add logic to handle the different types of search vs using the search bar
        self.searchBar.menu_data["Age"] = "Age"
        self.searchBar.menu_data["Attributes"] = ["Strength"]

class NameListTable(QTableWidget):

    refresh_panels = pyqtSignal()

    def __init__(self, parent=None, game_data: dict = None, dwarves: list[dict] = None):
        super().__init__(parent)
        font = QFont("More Perfect DOS VGA")
        self.setFont(font)
        self.setShowGrid(False)
        self.setColumnCount(1)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # for some reason the table font size is not
        # being set by by the central widget font
        font = self.font()
        font.setPointSize(6)
        self.setFont(font)

        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setHighlightSections(False)

        self.setStyleSheet(
            """QTableView::item:selected { \
                border: 3px solid gold; \
                background-color: transparent; \
                color: black; \
            }""")


    def populate_list(self, data: list[dict]):
        self.order = []
        self.setRowCount(len(data))
        print("populate")
        for i, entry in enumerate(data):
            item = QTableWidgetItem(f"{entry.get('first_name', 'Unknown')} {entry.get('last_name', '')}")
            self.setItem(i, 0, item)
            self.order.append(entry["id"])

        # select the first name in the list by default
        self.setCurrentCell(0, 0)
        self.refresh_panels.emit()