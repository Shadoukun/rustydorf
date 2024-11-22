
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QWidget, QLabel, QGridLayout, QAbstractItemView, QHeaderView

class DwarfInfoTabWidget(QWidget):
    def __init__(self, data: dict[list], row: int):
        super(DwarfInfoTabWidget, self).__init__()
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.infoSection = QtWidgets.QWidget(self)
        self.infoSection.setLayout(QGridLayout())
        self.infoSection.setObjectName("infoSection")

        self.thoughtsTable = QtWidgets.QTableWidget(self)
        self.thoughtsTable.setObjectName("thoughtsTable")

        self.attributeTable = QtWidgets.QTableWidget(self)
        self.attributeTable.setObjectName("attributeTable")

        self.traitTable = QtWidgets.QTableWidget(self)
        self.traitTable.setObjectName("traitTable")

        self.setup_info_section(data, row)
        self.setup_attribute_table(data, row)
        self.setup_trait_table(data, row)
        self.setup_thoughts_table(data, row)
        self.setup_beliefs_table(data, row)
        self.setup_goals_table(data, row)

        self.gridLayout.addWidget(self.infoSection, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.attributeTable, 0, 2, 2, 1)
        self.gridLayout.addWidget(self.traitTable, 0, 3, 2, 1)
        self.gridLayout.addWidget(self.thoughtsTable, 3, 0, 1, 4)

    def setup_info_section(self, data: list[dict], row: int):
        info = QLabel(f"Name: {data[row].get('first_name', 'Unknown')} {data[row].get('last_name', '')}\n" +
                      f"Profession: {data[row].get('profession', 'Unknown')['name']}\n" +
                      f"Age: {data[row].get('age', 'Unknown')}\n" +
                      f"Sex: {data[row].get('sex', 'Unknown')}")

        self.infoSection.layout().addWidget(info)

    def setup_attribute_table(self, data: list[dict], row: int):
        attributes: dict = data[row].get('attributes', {})

        self.attributeTable.verticalHeader().hide()
        self.attributeTable.horizontalHeader().hide()
        self.attributeTable.setColumnCount(2)
        self.attributeTable.setRowCount(len(attributes))

        attributes = sorted(attributes.items(), key=lambda item: item[1]["id"])

        for i, attribute in enumerate(attributes):
            name, value = attribute[1]['name'], attribute[1]['value']
            self.attributeTable.setItem(i, 0, QTableWidgetItem(name))
            self.attributeTable.setItem(i, 1, QTableWidgetItem(str(value)))


        # set the vertical header to resize to the contents and prevent the table from resizing
        # This feels janky but it works
        header = self.attributeTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.attributeTable.setFixedWidth(self.attributeTable.horizontalHeader().length() + 15)
        self.attributeTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.attributeTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.attributeTable.setSelectionMode(QAbstractItemView.NoSelection)


    def setup_trait_table(self, data: list[dict], row: int):
        traits = data[row].get('traits', [])

        self.traitTable.verticalHeader().hide()
        self.traitTable.horizontalHeader().hide()
        self.traitTable.setColumnCount(2)
        self.traitTable.setRowCount(len(traits))

        for i, trait in enumerate(traits):
            name, value = trait[0]['name'], trait[1]
            self.traitTable.setItem(i, 0, QTableWidgetItem(name))
            self.traitTable.setItem(i, 1, QTableWidgetItem(str(value)))

        # set the vertical header to resize to the contents and prevent the table from resizing
        # This feels janky but it works
        header = self.traitTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.traitTable.setFixedWidth(self.traitTable.horizontalHeader().length() + 15)
        self.traitTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)


        self.traitTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.traitTable.setSelectionMode(QAbstractItemView.NoSelection)

    def setup_thoughts_table(self, data: list[dict], row: int):
        thoughts = data[row].get('thoughts', [])

        self.thoughtsTable.verticalHeader().hide()
        self.thoughtsTable.horizontalHeader().hide()
        self.thoughtsTable.setColumnCount(1)
        self.thoughtsTable.setRowCount(len(thoughts))

        for i, thought in enumerate(thoughts):
            text = f"felt {thought['emotion_type'].lower()} {thought['thought']}"
            self.thoughtsTable.setItem(i, 0, QTableWidgetItem(text))

        self.thoughtsTable.resizeColumnsToContents()
        self.thoughtsTable.resizeRowsToContents()

        self.thoughtsTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.thoughtsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.thoughtsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.thoughtsTable.setSelectionMode(QAbstractItemView.NoSelection)

    def setup_beliefs_table(self, data: list[dict], row: int):
        beliefs = data[row].get('beliefs', [])

        beliefsTable = QTableWidget()
        beliefsTable.verticalHeader().hide()
        beliefsTable.horizontalHeader().hide()
        beliefsTable.setRowCount(len(beliefs))
        beliefsTable.setColumnCount(2)

        for i, belief in enumerate(beliefs):
            name, value = belief[0]['name'], str(belief[1])
            beliefsTable.setItem(i, 0, QTableWidgetItem(name))
            beliefsTable.setItem(i, 1, QTableWidgetItem(value))
        beliefsTable.resizeColumnsToContents()
        beliefsTable.resizeRowsToContents()

        # set the vertical header to resize to the contents and stretch the first column
        beliefsTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        beliefsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        beliefsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        beliefsTable.setSelectionMode(QAbstractItemView.NoSelection)

        self.infoSection.layout().addWidget(beliefsTable, 1, 0)

    def setup_goals_table(self, data: list[dict], row: int):
        goals = data[row].get('goals', [])

        goalsTable = QTableWidget()
        goalsTable.verticalHeader().hide()
        goalsTable.horizontalHeader().hide()
        goalsTable.setRowCount(len(goals))
        goalsTable.setColumnCount(2)

        for i, goal in enumerate(goals):
            name, value = goal[0]['name'], str(goal[1])
            goalsTable.setItem(i, 0, QTableWidgetItem(name))
            goalsTable.setItem(i, 1, QTableWidgetItem(value))

        goalsTable.resizeColumnsToContents()
        goalsTable.resizeRowsToContents()

        # set the vertical header to resize to the contents and stretch the first column
        goalsTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        goalsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        goalsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        goalsTable.setSelectionMode(QAbstractItemView.NoSelection)

        self.infoSection.layout().addWidget(goalsTable, 1, 1)
