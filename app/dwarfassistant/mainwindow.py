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

        self.mainPanel = QtWidgets.QStackedWidget(self.centralwidget)
        self.mainPanel.setObjectName("mainPanel")
        self.mainPanel.setContentsMargins(0, 0, 0, 0)

        self.gridLayout.addWidget(self.nameList, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.mainPanel, 1, 1, 1, 1)

        self.create_menu()
        self.connect_slots()
        self.nameList.nameTable.populate_list(self.dwarf_data)

        # select the first name in the list by default
        self.nameList.nameTable.setCurrentCell(0, 0)

    def update_task(self):
        # this is a func that will be called by the worker.
        def fn():
            # TODO: I can probably make Rust do this before calling populate_list or emitting a signal.
            game_data =  requests.get('http://127.0.0.1:3000/data')
            if game_data.status_code == 200:
                self.game_data = game_data.json()
            dwarf_data = requests.get('http://127.0.0.1:3000/dwarves')
            if dwarf_data.status_code == 200:
                self.dwarf_data = dwarf_data.json()

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
        self.nameList.searchBar.lineEdit().returnPressed.connect(self.filter_list)
        SignalsManager.instance().refresh_panels.connect(self.setup_main_panel)


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

    def filter_list(self):
        '''Filter the name list based on the search bar text.'''

        search_text = self.nameList.searchBar.lineEdit().text().lower()
        keywords = [r"@attr:"] # etc
        pattern = rf"({"|".join(keywords)})(.*)\W?"
        print("reg")
        # filter using keywords
        if matches := re.findall(pattern, search_text):
            print("match")
            result = {keyword: text for keyword, text in matches}

            for key in result.keys():
                sorted_list = []
                if key == "@attr:":
                    for d in self.dwarf_data:
                        for a in d["attributes"].values():
                            print(a)
                            if a["name"] == result[key].capitalize():
                                print(a["name"])
                                d["_sort_value"] = a["value"]
                                sorted_list.append(d)
                                break

                sorted_list = sorted(sorted_list, key=lambda d: d["_sort_value"], reverse=True)
                self.nameList.nameTable.populate_list(sorted_list)

    def show_labor_window(self):
        if self.labor_window is None:
            self.labor_window = LaborWindow(self.game_data, self.dwarf_data)
        self.labor_window.show()

    def get_game_data(self) -> dict:
        response: list[dict] = requests.get('http://127.0.0.1:3000/data').json()
        return response