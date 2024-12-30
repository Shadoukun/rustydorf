from PyQt6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QSizePolicy, QVBoxLayout
from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QFont

from .components.dropdowncombobox import DropdownComboBox
from .signals import SignalsManager

class NameListWidget(QWidget):
    """ The Main widget for the list of name list on the right side of the window."""
    def __init__(self, parent=None, game_data: dict = None, dwarves: list[dict] = None):
        super().__init__(parent)
        self.setObjectName("nameList")
        layout = QVBoxLayout()
        self.setLayout(layout)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setSizePolicy(sizePolicy)
        self.setMaximumWidth(150)

        # store the game data and the list of dwarves from the central widget for sorting
        self.game_data = game_data
        self.dwarves = dwarves

        # default sort key and order
        self.sort_key = "Name"
        self.ascending = False

        # the data for the search bar menu
        self.menu_data = {
            "Name": "Name",
            "Age": "Age",
            "Attributes": [a["name"] for a in game_data["attributes"]],
            "Traits": [t["name"] for t in game_data["traits"]],
            "Skills": [s["name"] for s in game_data["skills"]],
        }

        self.searchBar = NameListSearchBar(self, self.menu_data)
        self.searchBar.setObjectName("nameListSearchBar")
        self.searchBar.setPlaceholderText("Search")
        layout.addWidget(self.searchBar)

        self.nameTable = NameListTable(self, self.game_data, self.dwarves)
        self.nameTable.setObjectName("nameTable")
        layout.addWidget(self.nameTable)

        # This fixes an issue where styles/border colors would persist when the table cell selection changed. This forces the table to repaint when the current cell changes.
        self.nameTable.currentCellChanged.connect(lambda x: self.nameTable.viewport().update())

class NameListSearchBar(DropdownComboBox):
    """Search bar for the name list widget that uses a custom QComboBox to display a menu of search options."""
    #TODO: add ascending/descending
    def __init__(self, parent=None, menu_data: dict = None):
        super().__init__(parent)
        self.setPlaceholderText("Search")
        self.sortkey = ""
        self.menu_data = menu_data

    def showPopup(self):
        # instead of the default popup show a custom QMenu
        menu = QMenu(self)

        self.populate_menu(menu, self.menu_data)

        # position the menu below the combo box
        pos = self.mapToGlobal(QPoint(0, self.height()))
        action = menu.exec(pos)
        # if an action was triggered update the QComboBox text
        if action and action.data() is not None:
            # TODO: transform keywords, @attr, etc based on menu_data selection
            #       Or remove keywords. I'm not sure I need them. if I use this
            #
            #       I might keep keywords for goals/beliefs, etc that won't fit in the menu
            self.sortkey = action.text()
            SignalsManager.instance().sort_changed.emit(self.sortkey, False)


class NameListTable(QTableWidget):
    """The inner table widget for the name list"""
    def __init__(self, parent=None, game_data: dict = None, dwarves: list[dict] = None):
        super().__init__(parent)
        font = QFont("More Perfect DOS VGA")
        self.setFont(font)
        self.setShowGrid(False)
        self.setColumnCount(1)
        self.setRowCount(len(dwarves))
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