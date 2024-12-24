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

        self.sort_key = "Name"
        self.ascending = False
        self.menu_data = {
            "Name": "Name",
            "Age": "Age",
            "Attributes": [a["name"] for a in game_data["attributes"]],
            "Traits": [t["name"] for t in game_data["traits"]],
            "Skills": [s["name"] for s in game_data["skills"]],
        }

        self.game_data = game_data
        self.dwarves = dwarves

        self.searchBar = NameListSearchBar(self, self.menu_data)
        self.searchBar.setObjectName("nameListSearchBar")
        self.searchBar.setPlaceholderText("Search")
        layout.addWidget(self.searchBar)

        self.nameTable = NameListTable(self, self.game_data, self.dwarves)
        self.nameTable.setObjectName("nameTable")
        layout.addWidget(self.nameTable)

        SignalsManager.instance().sort_changed.connect(self.sort_data)

    def sort_data(self, key: str, ascending=False):
        """Sort the dwarves based on the given key and order, then reload the table."""

        self.sort_key = key
        self.ascending = ascending

        if key == "Name":
            sorted_data = sorted(self.dwarves, key=lambda x: x.get("first_name", "Unknown"), reverse=not ascending)

        elif key == "Age":
            sorted_data = sorted(self.dwarves, key=lambda x: x.get("age", 0), reverse=not ascending)

        elif key := next((a for a in self.game_data["attributes"] if a["name"] == key), None):
            sorted_data = self.sort_by_attribute(key, self.dwarves)

        elif key := next((t for t in self.game_data["traits"] if t["name"] == key), None):
            sorted_data = self.sort_by_trait(key, self.dwarves)

        elif key := next((s for s in self.game_data["skills"] if s["name"] == key), None):
            sorted_data = self.sort_by_skill(key, self.dwarves)

        else:
            # default to sorting by name
            sorted_data = sorted(self.dwarves, key=lambda x: x.get("first_name", "Unknown"), reverse=not ascending)

        self.nameTable.populate_list(sorted_data)

    @staticmethod
    def sort_by_attribute(dwarves: dict[list], key: str):
        sorted_list = []
        key = key.capitalize()
        for d in dwarves:
            attr = next((a for a in d["attributes"] if a["name"] == key), None)
            d["_sort_value"] = attr["value"]
            sorted_list.append(d)

        return sorted_list

    @staticmethod
    def sort_by_trait(dwarves: dict[list], key: str):
        sorted_list = []
        key = key.capitalize()
        for d in dwarves:
            trait = next((t for t in d["traits"] if t["name"] == key), None)
            d["_sort_value"] = trait["value"]
            sorted_list.append(d)

        return sorted_list

    @staticmethod
    def sort_by_skill(dwarves: dict[list], key: str):
        sorted_list = []
        key = key.capitalize()
        for d in dwarves:
            skill = next((s for s in d["skills"] if s["name"] == key), None)
            d["_sort_value"] = skill["value"]
            sorted_list.append(d)

        return sorted_list

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


    def populate_list(self, data: list[dict], emit=True):
        """Populate the name table with the given names."""
        self.order = []
        self.setRowCount(len(data))
        for i, entry in enumerate(data):
            item = QTableWidgetItem(f"{entry.get('first_name', 'Unknown')} {entry.get('last_name', '')}")
            self.setItem(i, 0, item)
            self.order.append(entry["id"])
