from PyQt5 import uic
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QWidget, QLabel, QGridLayout, QAbstractItemView, QHeaderView
from PyQt5.QtGui import QFont
import sys
import requests
from pprint import pprint

from app.namelist import NameListWidget
from app.dwarfinfotab import DwarfInfoTab

# Enable high DPI scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class DwarfAssistant(QMainWindow):

    def __init__(self, data: list[dict]):
        super(DwarfAssistant, self).__init__()
        # I guess do this here? clarity.
        self.game_data = self.get_game_data()

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

        self.nameList = NameListWidget(self.centralwidget, self.game_data, data)
        self.nameList.setObjectName("nameList")

        self.mainPanel = QtWidgets.QStackedWidget(self.centralwidget)
        self.mainPanel.setObjectName("mainPanel")
        self.mainPanel.setContentsMargins(0, 0, 0, 0)

        self.gridLayout.addWidget(self.nameList, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.mainPanel, 0, 1, 1, 1)

        self.nameList.populate_list(data)
        self.setup_main_panel(data)
        self.connect_slots()

    def connect_slots(self):
        self.nameList.itemSelectionChanged.connect(self.change_name_tab)

    def setup_main_panel(self, data: list[dict]):
        '''Create the main panel on the right side of the window.'''

        # Create tabs for each dwarf
        for row in range(self.nameList.rowCount()):
            self.mainPanel.addWidget(DwarfInfoTab(self.game_data, data, row, self.centralwidget))

    def change_name_tab(self):
        '''Change the dwarf tab when a new name is selected in the name list.'''

        selected_items = self.nameList.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            row = selected_item.row()
            self.mainPanel.setCurrentIndex(row)

    def get_game_data(self) -> dict:
        response: list[dict] = requests.get('http://127.0.0.1:3000/data').json()
        return response


if __name__ == '__main__':
    response = requests.get('http://127.0.0.1:3000/dwarves')
    data = response.json()
    app = QApplication(sys.argv)

    window = DwarfAssistant(data)
    window.show()
    sys.exit(app.exec_())