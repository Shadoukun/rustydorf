from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QAbstractItemView, QSizePolicy, QGridLayout, QWidget, QMenu
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class NameListWidget(QTableWidget):
    def __init__(self, parent=None, game_data: dict = None, dwarves: list[dict] = None):
        super(NameListWidget, self).__init__(parent)
        self.setObjectName("nameList")

        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        font = QFont("More Perfect DOS VGA")
        self.setFont(font)
        self.setSizePolicy(sizePolicy)
        self.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        self.setShowGrid(False)

        # for some reason the table font size is not
        # being set by by the central widget font
        font = self.font()
        font.setPointSize(6)
        self.setFont(font)

        self.setColumnCount(1)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setHighlightSections(False)

        self.setStyleSheet(
            """QTableView::item:selected { \
                border: 3px solid gold; \
                background-color: transparent; \
                color: black; \
            }""")

    def populate_list(self, data: list[dict]):
        self.setRowCount(len(data))
        for i, entry in enumerate(data):
            item = QTableWidgetItem(f"{entry.get('first_name', 'Unknown')} {entry.get('last_name', '')}")
            self.setItem(i, 0, item)

        # select the first name in the list by default
        self.setCurrentCell(0, 0)

    def contextMenuEvent(self, event):
            context_menu = QMenu(self)

            asc_sort = context_menu.addAction("Ascending")
            desc_sort= context_menu.addAction("Descending")

            # Execute the menu at the cursor position
            action = context_menu.exec_(self.mapToGlobal(event.pos()))

            # Handle the selected action
            if action == asc_sort:
                self.sort_table(ascending=True)
            elif action == desc_sort:
                self.sort_table(ascending=False)

    def sort_table(self, ascending=True):
        order = Qt.AscendingOrder if ascending else Qt.DescendingOrder
        self.sortItems(0, order)