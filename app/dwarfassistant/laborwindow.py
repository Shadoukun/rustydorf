import sys
import requests
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QApplication, QMainWindow, QTableWidgetItem, QWidget, QVBoxLayout, QGraphicsTextItem

from .components.checkboxtable import CheckboxTable, CheckBoxWidget
from .components.clickablegridview import ClickableGridView

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

        labor_view = LaborGridView(parent=self, data=data, dwarf_data=dwarf_data)
        self.setCentralWidget(labor_view)
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(labor_view)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

class LaborGridView(ClickableGridView):
    def __init__(self, parent=None, background_color=QColor(100, 100, 100), data: dict = None, dwarf_data: list[dict] = None):
        self.labors = sorted(data.get('labors', []), key=lambda x: x["id"])
        self.dwarves = dwarf_data
        cols = len(self.labors)
        rows = len(self.dwarves)

        headers = [labor["name"] for labor in self.labors]
        left_headers = [f"{dwarf['first_name']} {dwarf['last_name']}" for dwarf in self.dwarves]

        super().__init__(parent, rows, cols, 20,
                         background_color, headers, left_headers)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    response: list[dict] = requests.get('http://127.0.0.1:3000/data').json()
    dwarf_data = requests.get('http://127.0.0.1:3000/dwarves').json()

    main_window = LaborWindow(response, dwarf_data)
    main_window.resize(400, 300)
    main_window.show()
    sys.exit(app.exec())