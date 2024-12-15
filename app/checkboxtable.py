import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QCheckBox, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt

class CheckboxTable(QWidget):
    def __init__(self):
        super().__init__()
        self.table = QTableWidget()
        self.table.setRowCount(5)
        self.table.setColumnCount(3)
        layout = QHBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.populate_table()

        self.table.setStyleSheet("QTableWidget::item:selected { background-color: transparent; }")
        self.table.cellClicked.connect(self.toggle_checkbox)
        self.resize(400, 300)

    def populate_table(self) -> None:
        # list(map()) is nicer but its hard to read
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                # a hidden checkbox is used to track the state of the cell
                # I couldn't get the color changing to work if this is a separate class
                checkbox = QCheckBox()
                widget = QWidget()
                layout = QHBoxLayout()
                layout.addWidget(checkbox)
                layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
                checkbox.hide()

                self.table.setCellWidget(row, column, widget)
                checkbox.stateChanged.connect(lambda state, r=row, c=column: self.checkbox_state_changed(state, r, c))

    def toggle_checkbox(self, row, column) -> None:
        if (widget := self.table.cellWidget(row, column)) and (checkbox := widget.findChild(QCheckBox)):
            checkbox.setChecked(not checkbox.isChecked())

    def checkbox_state_changed(self, state, row, column) -> None:
        if state == Qt.CheckState.Checked.value:
            print(f"Checkbox at ({row}, {column}) is checked.")
            self.table.cellWidget(row, column).setStyleSheet("background-color: lightgreen;")
        else:
            print(f"Checkbox at ({row}, {column}) is unchecked.")
            self.table.cellWidget(row, column).setStyleSheet("background-color: none;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    checkbox_table = CheckboxTable()
    main_window.setCentralWidget(checkbox_table)
    main_window.setWindowTitle("QTableWidget with Checkboxes")
    main_window.resize(400, 300)
    main_window.show()
    sys.exit(app.exec())
