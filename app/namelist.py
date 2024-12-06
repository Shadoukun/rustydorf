from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QSizePolicy, QWidget, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal

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
        self.searchBar = QLineEdit(self)
        self.searchBar.setObjectName("searchBar")
        self.searchBar.setPlaceholderText("Search")
        self.searchBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.searchBar)

        self.nameTable = NameListTableWidget(self, self.game_data, self.dwarves)
        self.nameTable.setObjectName("nameTable")
        layout.addWidget(self.nameTable)

class NameListTableWidget(QTableWidget):

    refresh_panels = pyqtSignal()

    def __init__(self, parent=None, game_data: dict = None, dwarves: list[dict] = None):
        super().__init__(parent)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        font = QFont("More Perfect DOS VGA")
        self.setFont(font)
        self.setSizePolicy(sizePolicy)
        self.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        self.setShowGrid(False)

        # for some reason the table font size is not
        # being set by by the central widget font
        font = self.font()
        font.setPointSize(6)
        self.setFont(font)

        self.setColumnCount(1)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

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
        for i, entry in enumerate(data):
            item = QTableWidgetItem(f"{entry.get('first_name', 'Unknown')} {entry.get('last_name', '')}")
            self.setItem(i, 0, item)
            self.order.append(entry["id"])

        self.refresh_panels.emit()

        # select the first name in the list by default
        self.setCurrentCell(0, 0)

    # def contextMenuEvent(self, event):
    #     context_menu = QMenu(self)
    #
    #     # Create actions for sorting
    #     sort_name_asc_action = QAction('Name: Ascending', self)
    #     sort_name_desc_action = QAction('Name: Descending', self)
    #     sort_age_asc_action = QAction('Age: Ascending', self)
    #     sort_age_desc_action = QAction('Age: Descending', self)
    #
    #     sort_name_asc_action.triggered.connect(lambda: self.sort_data('first_name', True))
    #     sort_name_desc_action.triggered.connect(lambda: self.sort_data('first_name', False))
    #     sort_age_asc_action.triggered.connect(lambda: self.sort_data('age', True))
    #     sort_age_desc_action.triggered.connect(lambda: self.sort_data('age', False))
    #
    #     sort_menu = context_menu.addMenu("Sort")
    #     sort_menu.addAction(sort_name_asc_action)
    #     sort_menu.addAction(sort_name_desc_action)
    #     sort_menu.addAction(sort_age_asc_action)
    #     sort_menu.addAction(sort_age_desc_action)
    #
    #     attributes_menu = sort_menu.addMenu("Attributes")
    #     traits_menu = sort_menu.addMenu("Traits")
    #     skills_menu = sort_menu.addMenu("Skills")
    #
    #     context_menu.addMenu(sort_menu)
    #
    #     # Execute the menu at the cursor position
    #     context_menu.exec_(self.mapToGlobal(event.pos()))
    #
    # def sort_data(self, key: str, ascending=True):
    #     """Sort the data based on the given key and order, then reload the table."""
    #     sorted_data  = sorted(self.dwarves, key=lambda x: x.get(key, 0), reverse=not ascending)
    #     self.populate_list(sorted_data)
