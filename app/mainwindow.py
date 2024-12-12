import requests
from PyQt6.QtGui import QFont
from PyQt6 import QtWidgets

from .namelist import NameListWidget
from .dwarfinfotab import DwarfInfoTab


class DwarfAssistant(QtWidgets.QMainWindow):
    def __init__(self, data: list[dict]):
        super(DwarfAssistant, self).__init__()
        # I guess do this here? clarity.
        self.game_data = self.get_game_data()
        self.dwarf_data = data

        self.setWindowTitle("Dwarf Assistant")
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # Set font on central widget
        font = QFont()
        font.setPointSize(6)
        self.setFont(font)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setMenuBar(self.menubar)
        self.setStatusBar(self.statusbar)

        self.nameList = NameListWidget(self.centralwidget, self.game_data, self.dwarf_data)
        self.nameList.setObjectName("nameList")

        self.mainPanel = QtWidgets.QStackedWidget(self.centralwidget)
        self.mainPanel.setObjectName("mainPanel")
        self.mainPanel.setContentsMargins(0, 0, 0, 0)

        self.gridLayout.addWidget(self.nameList, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.mainPanel, 1, 1, 1, 1)

        self.nameList.nameTable.populate_list(self.dwarf_data)
        self.setup_main_panel()
        self.connect_slots()

    def connect_slots(self):
        self.nameList.nameTable.itemSelectionChanged.connect(self.change_name_tab)
        self.nameList.nameTable.refresh_panels.connect(self.setup_main_panel)

    def setup_main_panel(self):
        '''Create the main panel on the right side of the window.'''

        # Clear existing widgets
        while self.mainPanel.count():
            widget = self.mainPanel.currentWidget()
            self.mainPanel.removeWidget(widget)
            widget.deleteLater()

        # Create tabs for each dwarf from name list
        for row in self.nameList.nameTable.order:
            dwarf = next(dwarf for dwarf in self.dwarf_data if dwarf["id"] == row)
            self.mainPanel.addWidget(DwarfInfoTab(self.game_data, dwarf, self.centralwidget))

    def change_name_tab(self):
        '''Change the dwarf tab when a new name is selected in the name list.'''

        selected_items = self.nameList.nameTable.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            row = selected_item.row()
            self.mainPanel.setCurrentIndex(row)

    def get_game_data(self) -> dict:
        response: list[dict] = requests.get('http://127.0.0.1:3000/data').json()
        return response