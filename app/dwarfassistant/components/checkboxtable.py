import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QCheckBox, QWidget, QHBoxLayout, QHeaderView
from PyQt6.QtCore import Qt


class CheckboxTable(QWidget):
    def __init__(self):
        super().__init__()
        self.table = QTableWidget()
        self.table.setRowCount(5)
        self.table.setColumnCount(3)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.unchecked_stylesheet = "background-color: #933;"
        self.checked_stylesheet = "background-color: #393;"

        # override default section sizes to better match the checkbox size

        hheader = self.table.horizontalHeader()
        hheader.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        hheader.setMinimumSectionSize(15)

        vheader = self.table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        vheader.setMinimumSectionSize(15)

    def toggle_checkbox(self, row: int, column: int):
        if res := self.get_checkbox(row, column):
            _, checkbox = res
            if checkbox:
                checkbox.setChecked(not checkbox.isChecked())

    def get_checkbox(self, row: int, column: int) -> tuple[QWidget, QCheckBox]:
        """Get the checkbox widget at the specified row and column."""
        if (widget := self.table.cellWidget(row, column)) and (checkbox := widget.findChild(QCheckBox)):
                return widget, checkbox

    def checkbox_state_changed(self, state, row: int, column: int):
        match state:
            case Qt.CheckState.Checked.value:
                self.table.cellWidget(row, column).setStyleSheet(self.checked_stylesheet)
            case Qt.CheckState.Unchecked.value:
                self.table.cellWidget(row, column).setStyleSheet(self.unchecked_stylesheet)

    def populate_table(self):
        """override this method to populate the table with checkboxes"""
        hheader = self.table.horizontalHeader()
        vheader = self.table.verticalHeader()

        for row in range(self.table.rowCount()):
            vheader.setSectionResizeMode(row, QHeaderView.ResizeMode.Fixed)
            self.table.setRowHeight(row, 20)

            for column in range(self.table.columnCount()):
                hheader.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
                self.table.setColumnWidth(column, 20)
                checkbox_widget = CheckBoxWidget(self.table)
                self.table.setCellWidget(row, column, checkbox_widget)

                checkbox_widget.checkbox.stateChanged.connect(lambda state, row=row, column=column: self.checkbox_state_changed(state, row, column))


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
