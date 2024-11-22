from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QSizePolicy, QGridLayout

class NameListWidget(QWidget):
    def __init__(self, parent=None):
        super(NameListWidget, self).__init__(parent)
        self.setObjectName("table")
        self.table = QTableWidget(self)
        self.table.setObjectName("tableTable")

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        self.table.setSizePolicy(sizePolicy)
        self.table.setShowGrid(False)

        # for some reason the table font size is not
        # being set by by the central widget font
        font = self.table.font()
        font.setPointSize(6)
        self.table.setFont(font)

        self.table.setMaximumWidth(100)
        self.table.setColumnCount(1)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setHighlightSections(False)

        self.table.setStyleSheet(
            """QTableView::item:selected { \
                border: 3px solid gold; \
                background-color: transparent; \
                color: black; \
            }""")

        layout = QGridLayout(self)
        layout.addWidget(self.table, 0, 0, 1, 1)
        self.setLayout(layout)

