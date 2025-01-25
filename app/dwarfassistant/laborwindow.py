import sys
import requests
from PyQt6.QtGui import QFontMetrics, QStandardItemModel, QStandardItem, QColor

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QAbstractItemView, QGridLayout, QHeaderView, QApplication, QMainWindow, QTableWidgetItem, QWidget, QGraphicsTextItem, QVBoxLayout

from dwarfassistant.components.checkboxtable import CheckboxTable, CheckBoxWidget
from dwarfassistant.components.clickablegridview import ClickableGridView
from dwarfassistant.components.checkableangledtable import CheckableAngledTable, CheckedTableItemDelegate

WORK_DETAILS = {
    "Mining": {
        "color": "#393",
        "labors": [0]
    },
    "Woodworking": {
        "color": "#933",
        "labors": [11, 59]
    },
    "Stoneworking": {
        "color": "gray",
        "labors": [15, 12, 13, 14]
    },
    "Hunting/Related": {
        "color": "green",
        "labors": [16, 17, 44, 26, 27]
    },
    "Healthcare": {
        "color": "purple",
        "labors": [18, 19, 20, 21, 22, 23, 24]
    },
    "Farming/Related": {
        "color": "brown",
        "labors": [25, 29, 30, 34, 35, 36, 37, 38, 39, 40, 61, 62, 63, 64]
    },
    "Fishing/Related": {
        "color": "blue",
        "labors": [41, 42, 43]
    },
    "Metalsmithing": {
        "color": "darkgray",
        "labors": [45, 46, 47, 48, 49],
    },
    "Jewelry": {
        "color": "green",
        "labors": [50, 51],
    },
    "Crafts": {
        "color": "violet",
        "labors": [28, 52, 53, 54, 55, 32, 33, 56, 57, 58, 60, 67, 69, 70, 71, 72, 81, 82]
    },
    "Engineering": {
        "color": "orange",
        "labors": [57, 58, 60, 65]
    },
    "Hauling": {
        "color": "darkblue",
        "labors": [1, 2, 6, 3, 4, 5, 7, 8, 74, 77],
    },
    "Other": {
        "color": "black",
        "labors": [9, 10, 31, 66, 68, 73, 75, 76, 78, 79, 80]
    },
}


class LaborWindow(QMainWindow):
    def __init__(self, data: list[dict], dwarf_data: list[dict]):
        super().__init__()
        self.setWindowTitle("Dwarf Assistant: Labors")
        self.resize(800, 600)

        self.labor_table = CheckableAngledTable()
        self.setCentralWidget(self.labor_table)
        layout = QVBoxLayout()
        self.labor_table.setLayout(layout)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        labors = data["labors"]
        model = QStandardItemModel(len(dwarf_data),  len(labors))
        for i, dwarf in enumerate(dwarf_data):
            for j, labor in enumerate(labors):
                item = QStandardItem()
                item.setCheckable(True)

                enabled = dwarf["labors"][str(labor['id'])]["enabled"]
                item.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
                model.setItem(i, j, item)

        self.labor_table.setModel(model)
        self.labor_table.setItemDelegate(CheckedTableItemDelegate(self.labor_table))
        self.labor_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Set header labels
        model.setVerticalHeaderLabels([f'{dwarf["first_name"]} {dwarf["last_name"]}' for dwarf in dwarf_data])
        columns = [f'{labor["name"]}' for labor in labors]
        model.setHorizontalHeaderLabels(columns)
        self.labor_table.verticalHeader().setDefaultSectionSize(10)

        # Apply styles to headers and grid lines
        self.labor_table.setStyleSheet("""
            QHeaderView::section {
                background-color: gray;
                color: black;
                font-weight: bold;
                border: 1px solid #444;
            }
            QTableView {
                gridline-color: transparent;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    response: list[dict] = requests.get('http://127.0.0.1:3000/data').json()
    dwarf_data = requests.get('http://127.0.0.1:3000/dwarves').json()

    main_window = LaborWindow(response, dwarf_data)
    main_window.resize(400, 300)
    main_window.show()
    sys.exit(app.exec())