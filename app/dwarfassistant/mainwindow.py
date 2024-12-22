import re
import requests
import json
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6 import QtWidgets
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from .namelist import NameListWidget
from .dwarfinfotab import DwarfInfoTab
from .signals import SignalsManager
from .laborwindow import LaborWindow

from rustlib import RustWorker

API_URLS = [
            "http://127.0.0.1:3000/data",
            "http://127.0.0.1:3000/dwarves"
        ]

class NetworkWorker(QObject):

    dataReady = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.handleReply)

    def startAPIRequest(self, *args):
        for url in API_URLS:
            url = QUrl(url)
            request = QNetworkRequest(url)
            self.manager.get(request)

    def handleReply(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            try:
                url = reply.url().toString()
                data = reply.readAll().data().decode("utf-8")
                json_data = json.loads(data)

                if isinstance(json_data, list):
                    # If the data is a list, we need to wrap it in a dictionary to be able to emit it
                    dwarfdata = dict()
                    dwarfdata["dwarves"] = json_data
                    json_data = dwarfdata
                self.dataReady.emit(url, json_data)
            except json.JSONDecodeError:
                print("Error decoding JSON")
                return
        else:
            self.dataReady.emit("", f"Error: {reply.errorString()}")


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

        # Create a QNetworkAccessManager for making supposedly asynchronous backend requests
        self.network_worker = NetworkWorker()
        self.network_worker_thread = QThread()
        self.network_worker.moveToThread(self.network_worker_thread)
        self.network_worker_thread.start()
        self.network_worker.dataReady.connect(self.update_data)
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

        # create a timer to update the data every 5 seconds
        self.timer = QTimer(self)
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self.network_worker.startAPIRequest)
        self.timer.start()

    def update_data(self, url: str, data: str):
        if url == API_URLS[0]:
            self.game_data = data
        elif url == API_URLS[1]:
            # unwrap the dwarf list from the dictionary
            self.dwarf_data = data["dwarves"]
            self.nameList.nameTable.populate_list(self.dwarf_data)
            self.setup_main_panel

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        view_menu = menubar.addMenu("View")
        labor_view = view_menu.addAction("Labors")
        labor_view.triggered.connect(self.show_labor_window)

    def connect_slots(self):
        self.nameList.nameTable.itemSelectionChanged.connect(self.change_name_tab)

        SignalsManager.instance().refresh_panels.connect(self.setup_main_panel)

        self.nameList.searchBar.lineEdit().returnPressed.connect(self.filter_list)

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