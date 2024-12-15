import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QApplication, QMainWindow, QTableWidgetItem, QCheckBox
import requests
from checkboxtable import CheckboxTable

HEADERS = ["Woodworking", "Mining", "Fishing", "Your Mom"]

class RotatedHeaderView(QHeaderView):
    """A Custom header view that rotates the table header text 45 degrees counter-clockwise."""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

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

class LaborsTable(CheckboxTable):
    def __init__(self, data: list[dict], dwarf_data: list[dict]):
        self.labors = [labor['name'] for labor in data.get('labors', [])]
        self.dwarves = dwarf_data

        super().__init__()
        self.table.setHorizontalHeader(RotatedHeaderView(Qt.Orientation.Horizontal, self.table))
        self.table.horizontalHeader().setDefaultSectionSize(20)
        self.table.horizontalHeader().setFixedHeight(75)
        self.table.setRowCount(len(dwarf_data))
        self.table.setColumnCount(len(self.labors))
        self.populate_table()

    def populate_table(self):
        super().populate_table()
        for col, header in enumerate(self.labors):
            self.table.setHorizontalHeaderItem(col, QTableWidgetItem(header))

        for row, dwarf in enumerate(self.dwarves):
            for column, labor in enumerate(self.labors):
                if res := self.get_checkbox(row, column):
                    widget, checkbox = res
                    if checked := any([l["enabled"] for l in dwarf["labors"].values() if l["id"] == column]):
                        checkbox.setChecked(checked)
                        widget.setStyleSheet("background-color: lightgreen;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()

    response: list[dict] = requests.get('http://127.0.0.1:3000/data').json()
    dwarf_data = requests.get('http://127.0.0.1:3000/dwarves').json()

    labors_table = LaborsTable(response, dwarf_data)
    main_window.setCentralWidget(labors_table)
    main_window.setWindowTitle("Labors Table")
    main_window.resize(400, 300)
    main_window.show()
    sys.exit(app.exec())