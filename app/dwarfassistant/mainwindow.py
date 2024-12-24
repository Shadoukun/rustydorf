import re
import requests
from PyQt6.QtGui import QFont
from PyQt6 import QtWidgets

from .namelist import NameListWidget
from .dwarfinfotab import DwarfInfoTab
from .signals import SignalsManager
from .laborwindow import LaborWindow

# vscode seemingly doesn't/won't recognize this
from rustlib import RustWorker


API_URLS = [
            "http://127.0.0.1:3000/data",
            "http://127.0.0.1:3000/dwarves"
        ]

class DwarfAssistant(QtWidgets.QMainWindow):
    def __init__(self):
        super(DwarfAssistant, self).__init__()
        self.running = False

        # I guess do this here? clarity.
        self.game_data =  requests.get('http://127.0.0.1:3000/data').json()
        self.dwarf_data = requests.get('http://127.0.0.1:3000/dwarves').json()

        self.setWindowTitle("Dwarf Assistant")
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # Set font on central widget
        font = QFont()
        font.setPointSize(6)
        self.setFont(font)

        # create a worker to update the data.
        self.worker = RustWorker()
        self.worker.start(self.update_task(), 10)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setMenuBar(self.menubar)
        self.setStatusBar(self.statusbar)

        self.labor_window = None

        self.nameList = NameListWidget(self.centralwidget, self.game_data, self.dwarf_data)
        self.nameList.setObjectName("nameList")

        self.gridLayout.addWidget(self.nameList, 1, 0, 1, 1)
        self.nameList.nameTable.populate_list(self.dwarf_data)

        self.mainPanel = DwarfInfoTab(self.game_data, self.dwarf_data[0], self.centralwidget)
        self.mainPanel.setObjectName("mainPanel")
        self.mainPanel.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.addWidget(self.mainPanel, 1, 1, 1, 1)

        self.create_menu()
        self.connect_slots()

        # select the first name in the list by default
        self.nameList.nameTable.setCurrentCell(0, 0)

        # triggers the worker to start updating
        self.running = True

    def update_task(self):
        # this is a func that will be called by the worker.
        def fn():
            if not self.running:
                return

            # TODO: I can probably make Rust do this before calling populate_list or emitting a signal.
            game_data =  requests.get('http://127.0.0.1:3000/data')
            if game_data.status_code == 200:
                self.game_data = game_data.json()
            dwarf_data = requests.get('http://127.0.0.1:3000/dwarves')
            if dwarf_data.status_code == 200:
                self.dwarf_data = dwarf_data.json()

            if self.nameList.sort_key:
                self.nameList.sort_data(self.nameList.sort_key, self.nameList.ascending)
            else:
                self.nameList.nameTable.populate_list(self.dwarf_data, False)

        return fn

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        view_menu = menubar.addMenu("View")
        labor_view = view_menu.addAction("Labors")
        labor_view.triggered.connect(self.show_labor_window)

    def connect_slots(self):
        self.nameList.nameTable.itemSelectionChanged.connect(self.change_name_tab)
        self.nameList.searchBar.lineEdit().returnPressed.connect(self.sort_list)
        SignalsManager.instance().sort_changed.connect(self.change_name_tab)

    def change_name_tab(self):
        '''Change the dwarf tab when a new name is selected in the name list.'''
        # remove the current main panel
        if self.mainPanel is not None:
            self.layout().removeWidget(self.mainPanel)
            self.mainPanel.deleteLater()
            self.mainPanel = None

        selected_items = self.nameList.nameTable.selectedItems()
        if not selected_items:
            return

        if dwarf := next((d for d in self.dwarf_data if d["first_name"] == selected_items[0].text().split(" ")[0]), None):
            self.mainPanel = DwarfInfoTab(self.game_data, dwarf, self.centralwidget)
            self.mainPanel.setObjectName("mainPanel")
            self.gridLayout.addWidget(self.mainPanel, 1, 1, 1, 1)

    def sort_list(self):
        '''Filter the name list based on the search bar text.'''
        search_text = self.nameList.searchBar.lineEdit().text().lower()
        keywords = [r"@attr:"] # etc
        result = self.get_sort_key_value(search_text, keywords)

        sorted_list = []

        # only use the first key for now
        sort_key, value = list(result.items())[0]
        if not sort_key:
            return

        if sort_key == "@attr:":
            sorted_list = self.sort_by_attribute(value)

        sorted_list = sorted(sorted_list, key=lambda d: d["_sort_value"], reverse=True)
        print(sorted_list)
        self.nameList.nameTable.populate_list(sorted_list)
        self.change_name_tab()

    def get_sort_key_value(self, search_text: str, keywords: list):
        '''Get the filter key from the search text.'''
        result = {}
        pattern = rf"({"|".join(keywords)})(.*)\W?"

        if matches := re.findall(pattern, search_text):
            result = {keyword: text for keyword, text in matches}

        return result

    def show_labor_window(self):
        if self.labor_window is None:
            self.labor_window = LaborWindow(self.game_data, self.dwarf_data)
        self.labor_window.show()
