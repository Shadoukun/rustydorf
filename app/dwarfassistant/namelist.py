from typing import Tuple
from PyQt6.QtWidgets import QWidget, QTableWidget, QAbstractItemView, QSizePolicy, QVBoxLayout, QLabel, QTableWidgetItem, QHBoxLayout
from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import Qt, QPoint, QSettings
from PyQt6.QtGui import QFont

from .components.dropdowncombobox import DropdownComboBox, SortComboBox
from .signals import SignalsManager


STYLESHEET = '''
QComboBox {
    border: 0px;
    border-radius: 3px;
    padding: 1px 18px 1px 3px;
    min-width: 6em;
    background: palette(Base);
}

QComboBox:focus {
    border: 1px solid darkgray;
    padding-top: 3px;
    padding-left: 4px;
    background: palette(Mid);
}

QComboBox::drop-down {
    width: 25px;
    margin-left: 0px;
    border-left: 1px solid #a0a0a4;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
}

QMenu {
    background-color: palette(Base);
    border: 1px solid darkgray;
}

QMenu::item {
    background-color: transparent;
    padding: 5px 10px;
}

QMenu::item:selected {
    background-color: palette(Mid);
}

QPushButton {
    border: none;
    border-radius: 0px;
    padding: 0px;
    color: white;
    background-color: transparent;
}

QPushButton:hover {
    background-color: transparent;
}

QTableView::item {
    padding: 5px;
    background-color: transparent;
    border: 0px;
}

QTableView::item:selected {
    border: 3px solid gold;
}

QLabel#professionLabel {
    color: rgb(150, 150, 150);
}
'''

class NameListWidget(QWidget):
    """
    This is the widget that contains the search bar and name table on the left side of the main window.
    """

    def __init__(self, parent=None, game_data: dict = None, dwarves: list[dict] = None, settings: QSettings = None):
        super().__init__(parent)
        self.setObjectName("nameList")
        layout = QVBoxLayout()
        self.setLayout(layout)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setSizePolicy(sizePolicy)

        # TODO: variable width based on font size
        # do sizing with nameTable instead?
        self.setMinimumWidth(200)

        # for some reason the font size is not being set by the parent font
        font_name = settings.value("font_name", "More Perfect DOS VGA", type=str)
        font_size = settings.value("font_size", 6, type=int)
        font = QFont(font_name, font_size)
        self.setFont(font)

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

        searchBarWidget = QWidget(self)
        searchBarWidget.setObjectName("searchBarWidget")

        searchbarlayout = QHBoxLayout(searchBarWidget)
        searchbarlayout.setContentsMargins(0, 0, 0, 0)
        searchBarWidget.setLayout(searchbarlayout)
        layout.addWidget(searchBarWidget)

        self.searchBar = SortComboBox(self, NameListSearchBar(self, self.menu_data))
        self.searchBar.setObjectName("nameListSearchBar")
        self.searchBar.combo.setFixedHeight(30)
        self.searchBar.font().setPointSize(settings.value("font_size", 6, type=int))
        searchbarlayout.addWidget(self.searchBar)

        self.nameTable = NameListTable(self)
        self.nameTable.setObjectName("nameTable")
        self.nameTable.setColumnCount(2)

        column_width = 150
        self.nameTable.setColumnWidth(0, column_width)
        self.nameTable.setColumnHidden(1, True)
        layout.addWidget(self.nameTable)

        self.nameTable.setMinimumWidth(column_width + 2)
        self.setStyleSheet(STYLESHEET)

    def get_selection(self) -> Tuple[int, QTableWidgetItem]:
        """Get the selected row from the namelist table and return the QTableWidgetItem object for the dwarf id

           This takes the selected cell from the table and returns the QTableWidgetItem that contains
           the dwarf id from the hidden adjacent column.
        """

        # use selectedIndexes() to get the selected row because selectedItems() AND currentRow() are jank
        # - selectedItems() returns None because we are using setCellWidget() and not a QTableWidgetItem with setItem()
        # - currentRow() does not return to 0 when the user clicks and drags their selection,
        #   even if the selection returns to the first row

        # in this case, selectedIndexes always returns a list of 1 index (the selected row)
        row = self.nameTable.selectionModel().selectedIndexes()[0].row()
        selected_id = self.nameTable.item(row, 1)

        if selected_id is not None:
            return row, selected_id

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
        menu.setFixedWidth(self.width())
        self.populate_menu(menu, self.menu_data)
        pos = self.mapToGlobal(QPoint(0, self.height()))
        # if an action was triggered update the QComboBox text
        if (action := menu.exec(pos)) and action.data() is not None:
            # TODO: transform keywords, @attr, etc based on menu_data selection
            #       Or remove keywords. I'm not sure I need them. if I use this
            #
            #       I might keep keywords for goals/beliefs, etc that won't fit in the menu
            self.sortkey = action.text()
            SignalsManager.instance().sort_changed.emit(self.sortkey, False)


class NameListTable(QTableWidget):
    """The inner table widget for the name list"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setShowGrid(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setHighlightSections(False)
        self.verticalHeader().setDefaultSectionSize(40)

class NameListLabel(QWidget):
    def __init__(self, entry: dict, parent=None, font: QFont = None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        name_label = QLabel(f"{entry.get('first_name', 'Unknown')} {entry.get('last_name', '')}")
        layout.addWidget(name_label)

        profession = entry.get('profession', {}).get('name', 'Unknown')
        profession_label = QLabel(profession)
        profession_label.setObjectName("professionLabel")
        self.setFont(font)
        profession_label.setFont(font)
        layout.addWidget(profession_label)