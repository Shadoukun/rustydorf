import sys
import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QApplication, QMainWindow, QTableWidgetItem, QWidget, QVBoxLayout

from .components.checkboxtable import CheckboxTable, CheckBoxWidget

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


# class LaborSection(QWidget):
#     def __init__(self, data: dict):
#         super().__init__()
#         self.labors = data.get('labors', [])
#         self.dwarves = data.get('dwarves', [])
#         self.table = CheckboxTable()
#         self.table.setRowCount(len(self.dwarves))
#         self.table.setColumnCount(len(self.labors))
#         self.populate_table()


class LaborWindow(QMainWindow):
    def __init__(self, data: list[dict], dwarf_data: list[dict]):
        super().__init__()
        self.setWindowTitle("Dwarf Assistant: Labors")
        self.resize(800, 600)
        labors_table = LaborTable(data, dwarf_data)
        self.setCentralWidget(labors_table)
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(labors_table)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


class RotatedHeaderView(QHeaderView):
    """A Custom header view that rotates the table header text 45 degrees counter-clockwise."""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
        QHeaderView::section:hover {
            background-color: none;
            }
        """)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        painter.translate(rect.center())
        painter.rotate(-45)
        painter.translate(-rect.center())

        # Adjust rect for rotated text
        adjusted_rect = rect.adjusted(-20, 10, 20, 20)  # Add padding for rotated text
        painter.drawText(
            adjusted_rect, Qt.AlignmentFlag.AlignCenter, self.model().headerData(logicalIndex, self.orientation())
        )
        painter.restore()


class LaborTable(CheckboxTable):
    def __init__(self, data: list[dict], dwarf_data: list[dict]):
        # load data before calling super().__init__()
        self.labors = sorted(data.get('labors', []), key=lambda x: x["id"])
        self.dwarves = dwarf_data
        super().__init__()

        self.table.setRowCount(len(dwarf_data))
        self.table.setColumnCount(len(self.labors))
        self.table.setHorizontalHeader(RotatedHeaderView(Qt.Orientation.Horizontal, self.table))
        self.populate_table()

    def populate_table(self):
        hheader = self.table.horizontalHeader()
        hheader.setDefaultSectionSize(20)
        vheader = self.table.verticalHeader()
        vheader.setDefaultSectionSize(20)

        for row, dwarf in enumerate(self.dwarves):
            # important for checkbox size
            vheader.setSectionResizeMode(row, QHeaderView.ResizeMode.Fixed)
            self.table.setRowHeight(row, 20)

            sorted_labors = sorted(dwarf["labors"].items(), key=lambda x: x[1]["id"])
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(f"{dwarf['first_name']} {dwarf['last_name']}"))

            for column, labor in enumerate(self.labors):
                # important for checkbox size
                hheader.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
                self.table.setColumnWidth(column, 20)

                self.table.setHorizontalHeaderItem(column, QTableWidgetItem(labor["name"]))

                # use custom checkbox widget
                checkbox = CheckBoxWidget(self.table)
                # Check if the labor is enabled for the dwarf
                if checked := sorted_labors[column][1]["enabled"]:
                    checkbox.checkbox.setChecked(checked)
                    checkbox.setStyleSheet("background-color: #393;")
                else:
                    checkbox.setStyleSheet("background-color: #933;")

                self.table.setCellWidget(row, column, checkbox)
                checkbox.checkbox.stateChanged.connect(lambda state, r=row, c=column: self.checkbox_state_changed(state, r, c))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()

    response: list[dict] = requests.get('http://127.0.0.1:3000/data').json()
    dwarf_data = requests.get('http://127.0.0.1:3000/dwarves').json()

    labors_table = LaborTable(response, dwarf_data)
    main_window.setCentralWidget(labors_table)
    main_window.setWindowTitle("Labors Table")
    main_window.resize(400, 300)
    main_window.show()
    sys.exit(app.exec())