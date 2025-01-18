import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QCheckBox, QWidget, QHBoxLayout, QHeaderView, QLabel
from PyQt6.QtCore import Qt

class CheckboxTable(QWidget):
    def __init__(self):
        super().__init__()
        self.table = QTableWidget()
        self.table.setRowCount(5)
        self.table.setColumnCount(3)

        hheader = self.table.horizontalHeader()
        hheader.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        hheader.setMinimumSectionSize(15)

        vheader = self.table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        vheader.setMinimumSectionSize(15)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.populate_table()

        self.table.cellClicked.connect(self.toggle_checkbox)
        self.resize(400, 300)

    def toggle_checkbox(self, row: int, column: int) -> None:
        if res := self.get_checkbox(row, column):
            _, checkbox = res
            if checkbox:
                checkbox.setChecked(not checkbox.isChecked())

    def get_checkbox(self, row: int, column: int) -> tuple[QWidget, QCheckBox]:
        """Get the checkbox widget at the specified row and column."""
        if (widget := self.table.cellWidget(row, column)) and (checkbox := widget.findChild(QCheckBox)):
                return widget, checkbox
        else:
            return None, None

    def checkbox_state_changed(self, state, row, column) -> None:
        if state == Qt.CheckState.Checked.value:
            print(f"Checkbox at ({row}, {column}) is checked.")
            self.table.cellWidget(row, column).setStyleSheet("background-color: #393;")
        else:
            print(f"Checkbox at ({row}, {column}) is unchecked.")
            self.table.cellWidget(row, column).setStyleSheet("background-color: #933;")

    def populate_table(self):
        hheader = self.table.horizontalHeader()
        vheader = self.table.verticalHeader()

        for row in range(self.table.rowCount()):
            vheader.setSectionResizeMode(row, QHeaderView.ResizeMode.Fixed)
            self.table.setRowHeight(row, 20)

            for column in range(self.table.columnCount()):
                hheader.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
                self.table.setColumnWidth(column, 20)
                checkbox_widget = CheckBoxWidget(self.table)
                checkbox_widget.checkbox.stateChanged.connect(lambda state, row=row, column=column: self.checkbox_state_changed(state, row, column))
                self.table.setCellWidget(row, column, checkbox_widget)

class CheckBoxWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkbox = QCheckBox()
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.checkbox)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    checkbox_table = CheckboxTable()
    main_window.setCentralWidget(checkbox_table)
    main_window.setWindowTitle("QTableWidget with Checkboxes")
    main_window.resize(400, 300)
    main_window.show()
    sys.exit(app.exec())
