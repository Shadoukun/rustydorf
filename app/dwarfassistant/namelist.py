from typing import Tuple
from PyQt6.QtWidgets import QWidget, QTableWidget, QAbstractItemView, QSizePolicy, QVBoxLayout, QLabel, QTableWidgetItem
from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import Qt, QPoint, QSettings
from PyQt6.QtGui import QFont

from .components.dropdowncombobox import DropdownComboBox
from .signals import SignalsManager

class NameListWidget(QWidget):
    """ The Main widget for the list of name list on the right side of the window."""
    def __init__(self, parent=None, game_data: dict = None, dwarves: list[dict] = None, settings: QSettings = None):
        super().__init__(parent)
        self.setObjectName("nameList")
        layout = QVBoxLayout()
        self.setLayout(layout)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setSizePolicy(sizePolicy)
        self.setMaximumWidth(150)

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

        self.searchBar = NameListSearchBar(self, self.menu_data)
        self.searchBar.setObjectName("nameListSearchBar")
        self.searchBar.setPlaceholderText("Search")
        layout.addWidget(self.searchBar)

        self.nameTable = NameListTable(self)
        self.nameTable.setObjectName("nameTable")
        self.nameTable.setColumnCount(2)
        self.nameTable.setColumnHidden(1, True)
        layout.addWidget(self.nameTable)

        # This fixes an issue where styles/border colors would persist when the table cell selection changed.
        # This forces the table to repaint when the current cell changes.
        self.nameTable.currentCellChanged.connect(lambda x: self.nameTable.viewport().update())

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

        existing = self.styleSheet()
        self.setStyleSheet(existing +
            """
            QTableView::item { \
                padding: 5px; \
                background-color: transparent; \
                border: 0px; \
            } \

            QTableView::item:selected { \
                border: 3px solid gold; \
            }""")

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
        profession_label.setStyleSheet("color: rgb(150, 150, 150);")
        self.setFont(font)
        profession_label.setFont(font)
        layout.addWidget(profession_label)