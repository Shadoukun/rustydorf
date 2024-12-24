import sys
import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QApplication, QMainWindow, QTableWidgetItem, QCheckBox, QWidget, QVBoxLayout

from .components.checkboxtable import CheckboxTable


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
        # list(map()) is nicer but its hard to read
        for row, dwarf in enumerate(self.dwarves):
            # Set the vertical header to the dwarf's name
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(f"{dwarf['first_name']} {dwarf['last_name']}"))
            for column, labor in enumerate(self.labors):
                # set the horizontal header to the labor name
                self.table.setHorizontalHeaderItem(column, QTableWidgetItem(labor))

                # Create a checkbox widget for each labor
                checkbox = QCheckBox()
                widget = QWidget()
                layout = QVBoxLayout()
                layout.addWidget(checkbox)
                layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
                checkbox.hide()

                # Check if the labor is enabled for the dwarf
                if checkbox:
                    if checked := any([labor["enabled"] for labor in dwarf["labors"].values() if labor["id"] == column]):
                        checkbox.setChecked(checked)
                        widget.setStyleSheet("background-color: #393;")
                    else:
                        widget.setStyleSheet("background-color: #933;")

                self.table.setCellWidget(row, column, widget)
                checkbox.stateChanged.connect(lambda state, r=row, c=column: self.checkbox_state_changed(state, r, c))


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