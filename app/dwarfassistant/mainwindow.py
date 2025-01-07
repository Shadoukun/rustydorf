import re
import requests
from PyQt6.QtGui import QFont
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import QSettings

from .namelist import NameListWidget, NameListLabel
from .dwarfinfotab import DwarfInfoTab
from .signals import SignalsManager
from .laborwindow import LaborWindow
from .settingsmenu import SettingsMenuDialog

# vscode seemingly doesn't/won't recognize this
from rustlib import RustWorker

API_URLS = {
    "data": "http://127.0.0.1:3000/data",
    "dwarves": "http://127.0.0.1:3000/dwarves"
}


class DwarfAssistant(QtWidgets.QMainWindow):
    def __init__(self):
        super(DwarfAssistant, self).__init__()
        self.running = False

        self.settings = QSettings("DwarfAssistant", "DwarfAssistant")
        self.game_data =  requests.get(API_URLS["data"]).json()
        self.dwarf_data = requests.get(API_URLS["dwarves"]).json()

        # create a worker to update the data.
        self.worker = RustWorker()
        self.start_update_worker()

        # Initialize the main window
        self.setWindowTitle("Dwarf Assistant")
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        font = QFont()
        font.setPointSize(self.settings.value("font_size", 6, type=int))
        self.setFont(font)

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

        self.mainPanel = DwarfInfoTab(self.game_data, self.dwarf_data[0], self.centralwidget)
        self.mainPanel.setObjectName("mainPanel")
        self.mainPanel.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.addWidget(self.mainPanel, 1, 1, 1, 1)

        self.create_menu()
        self.connect_slots()

        # default sort key and order
        self.sort_key = "Name"
        SignalsManager.instance().sort_changed.emit(self.sort_key, False)
        self.nameList.nameTable.setCurrentCell(0, 0) # select the first cell in the name list

        self.running = True

    def start_update_worker(self):
        # the callback that will be run by the worker
        def fn():
            if not self.running:
                return

            dwarf_data = None
            game_data =  requests.get(API_URLS["data"])
            if game_data.status_code == 200:
                self.game_data = game_data.json()

            dwarf_data = requests.get(API_URLS["dwarves"])
            if dwarf_data.status_code == 200:
                dwarf_data = dwarf_data.json()
                # don't update the list if there are no changes
                # TODO: This is a simple check right now.
                # If a dwarf leaves and then another one arrives immediately after,
                # it won't update the list
                if len(dwarf_data) != len(self.dwarf_data):
                    self.dwarf_data = dwarf_data
                    self.sort_and_populate(self.sort_key, self.nameList.ascending)

        # start the worker
        self.worker.start(fn, 10)

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        settings_action = file_menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings_window)

        view_menu = menubar.addMenu("View")
        labor_view = view_menu.addAction("Labors")
        labor_view.triggered.connect(self.show_labor_window)

    def connect_slots(self):
        """Connect the signals to the slots."""
        signal_manager = SignalsManager.instance()
        self.nameList.nameTable.itemSelectionChanged.connect(self.change_name_tab)
        self.nameList.searchBar.lineEdit().returnPressed.connect(self.sort_list)

        # signals
        signal_manager.sort_changed.connect(self.sort_and_populate)
        signal_manager.populate_table.connect(self.populate_name_list)

    def change_name_tab(self):
        '''Change the dwarf tab when a new name is selected in the name list.'''
        # remove the current main panel otherwise it will stack behind the new one
        if self.mainPanel is not None:
            self.layout().removeWidget(self.mainPanel)
            self.mainPanel.deleteLater()
            self.mainPanel = None

        # get the selected dwarf from the name list by id
        if selection := self.nameList.get_selection():
            if dwarf := next((d for d in self.dwarf_data if d["id"] == int(selection.text())), None):
                self.mainPanel = DwarfInfoTab(self.game_data, dwarf, self.centralwidget)
                self.mainPanel.setObjectName("mainPanel")
                self.gridLayout.addWidget(self.mainPanel, 1, 1, 1, 1)

    def populate_name_list(self, data: list[dict]):
        """Populate the name table with the given names."""
        self.nameList.nameTable.setRowCount(len(data))
        for i, entry in enumerate(data):
            self.nameList.nameTable.setCellWidget(i, 0, NameListLabel(entry))
            self.nameList.nameTable.setItem(i, 1, QTableWidgetItem(str(entry["id"])))

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
        SignalsManager.instance().populate_table.emit(sorted_list)

    def get_sort_key_value(self, search_text: str, keywords: list):
        '''Get the filter key from the search text.'''
        result = {}
        pattern = rf"({"|".join(keywords)})(.*)\W?"

        if matches := re.findall(pattern, search_text):
            result = {keyword: text for keyword, text in matches}

        return result

    def sort_and_populate(self, key: str, descending=False):
        """Sort the dwarves based on the given key and order, then reload the table."""
        print(f"Sorting by {key} in descending order: {descending}")
        self.sort_key = key
        self.descending = descending

        if key == "Name":
            sorted_data = sorted(self.dwarf_data, key=lambda x: x.get("first_name", "Unknown"), reverse=self.descending)

        elif key == "Age":
            sorted_data = sorted(self.dwarf_data, key=lambda x: x.get("age", 0), reverse=not self.descending)

        elif key := next((a for a in self.game_data["attributes"] if a["name"] == self.sort_key), None):
            sorted_data = self.sort_by_attribute(self.dwarf_data, self.sort_key, not self.descending)

        elif key := next((t for t in self.game_data["traits"] if t["name"] == self.sort_key), None):
            sorted_data = self.sort_by_trait(self.dwarf_data, self.sort_key, not self.descending)

        elif key := next((s for s in self.game_data["skills"] if s["name"] == self.sort_key), None):
            sorted_data = self.sort_by_skill(self.dwarf_data, self.sort_key, not self.descending)

        else:
            # default to sorting by name
            sorted_data = sorted(self.dwarf_data, key=lambda x: x.get("first_name", "Unknown"), reverse=self.descending)

        SignalsManager.instance().populate_table.emit(sorted_data)

    @staticmethod
    def sort_by_attribute(dwarves, key: str, descending: bool):
        for d in dwarves:
            attr = next((a for a in d["attributes"].values() if a["name"] == key), None)
            d["_sort_value"] = attr["value"]

        return sorted(dwarves, key=lambda x: x["_sort_value"], reverse=descending)

    @staticmethod
    def sort_by_trait(dwarves: dict[list], key: str, descending: bool):
        # traits are [id, name, value]
        for d in dwarves:
            trait = next((t for t in d["traits"] if t[1] == key), None)
            d["_sort_value"] = trait[2]

        return sorted(dwarves, key=lambda x: x["_sort_value"], reverse=descending)

    @staticmethod
    def sort_by_skill(dwarves: dict[list], key: str, descending: bool):
        for d in dwarves:
            skill = next((a for a in d["skills"] if a["name"] == key), None)
            d["_sort_value"] = skill["experience"] if skill else 0

        return sorted(dwarves, key=lambda x: x["_sort_value"], reverse=descending)

    def show_labor_window(self):
        if self.labor_window is None:
            self.labor_window = LaborWindow(self.game_data, self.dwarf_data)
        self.labor_window.show()

    def show_settings_window(self):
        settings_window = SettingsMenuDialog(settings=self.settings)
        settings_window.exec()