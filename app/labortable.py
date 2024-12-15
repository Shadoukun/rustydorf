import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QApplication, QMainWindow, QTableWidgetItem
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
    def __init__(self):
        super().__init__()
        self.table.setHorizontalHeader(RotatedHeaderView(Qt.Orientation.Horizontal, self.table))
        self.table.horizontalHeader().setDefaultSectionSize(20)
        self.table.horizontalHeader().setFixedHeight(75)
        self.table.setRowCount(5)
        self.table.setColumnCount(4)
        self.populate_table()

    def populate_table(self):
        super().populate_table()
        for col, header in enumerate(HEADERS):
            self.table.setHorizontalHeaderItem(col, QTableWidgetItem(header))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    labors_table = LaborsTable()
    main_window.setCentralWidget(labors_table)
    main_window.setWindowTitle("QTableWidget with Rotated Headers")
    main_window.resize(400, 300)
    main_window.show()
    sys.exit(app.exec())