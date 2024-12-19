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

    def toggle_checkbox(self, row: int, column: int) -> None:
        if res := self.get_checkbox(row, column):
            _, checkbox = res
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    checkbox_table = CheckboxTable()
    main_window.setCentralWidget(checkbox_table)
    main_window.setWindowTitle("QTableWidget with Checkboxes")
    main_window.resize(400, 300)
    main_window.show()
    sys.exit(app.exec())
