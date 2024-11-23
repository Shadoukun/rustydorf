from PyQt5 import uic
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QWidget, QLabel, QGridLayout, QAbstractItemView, QHeaderView
from PyQt5.QtGui import QFont
import sys
import requests

from app.namelist import NameListWidget
from app.dwarftab import DwarfTabWidget

# Enable high DPI scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

class DwarfAssistant(QMainWindow):

    def __init__(self, data: list[dict]):
        super(DwarfAssistant, self).__init__()
        self.setWindowTitle("Dwarf Assistant")

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        # Set font on central widget
        font = QFont()
        font.setPointSize(6)
        self.setFont(font)

        self.setup_menu_bar()
        self.setup_name_list(data)
        self.setup_main_panel(data)

        # select the first name in the list by default
        self.nameList.table.setCurrentCell(0, 0)
        self.nameList.table.itemSelectionChanged.connect(self.change_tab)

    def setup_menu_bar(self):
        # Create empty menu bar and status bar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")

        self.setMenuBar(self.menubar)
        self.setStatusBar(self.statusbar)

    def setup_name_list(self, data: list[dict]):
        '''populate the table of names on the left side of the window.'''

        self.nameList = NameListWidget(self.centralwidget)
        self.nameList.table.setRowCount(len(data))
        for i, entry in enumerate(data):
            item = QTableWidgetItem(f"{entry.get('first_name', 'Unknown')} {entry.get('last_name', '')}")
            self.nameList.table.setItem(i, 0, item)

        self.gridLayout.addWidget(self.nameList, 0, 0, 1, 1)


    def setup_main_panel(self, data: list[dict]):
        '''Create the main panel on the right side of the window.'''

        self.mainPanel = QtWidgets.QTabWidget(self.centralwidget)
        self.mainPanel.setObjectName("mainPanel")

        # Create tabs for each dwarf
        for row in range(self.nameList.table.rowCount()):
            # the tab widget doesn't need to have tab titles,
            # so pass an empty string
            self.mainPanel.addTab(DwarfTabWidget(data, row), "")

        self.mainPanel.tabBar().hide()
        self.gridLayout.addWidget(self.mainPanel, 0, 1, 1, 1)
        self.adjustSize()


    def change_tab(self):
        '''Change the tab when a new name is selected in the name list.'''

        selected_items = self.nameList.table.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            row = selected_item.row()
            self.mainPanel.setCurrentIndex(row)


if __name__ == '__main__':
    response = requests.get('http://127.0.0.1:3000/dwarves')
    data = response.json()
    app = QApplication(sys.argv)

    window = DwarfAssistant(data)
    window.show()
    sys.exit(app.exec_())