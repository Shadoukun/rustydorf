from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt5.QtCore import Qt


class DwarfInfoTab(QtWidgets.QWidget):
    def __init__(self, game_data: dict, data: dict[list], row: int, parent=None):
        super().__init__(parent)
        uic.loadUi('app/dwarfinfotab.ui', self)
        self.infoLabel.setText(f"Name: {data[row].get('first_name', 'Unknown')} {data[row].get('last_name', '')}\n" +
                                f"Profession: {data[row].get('profession', 'Unknown')['name']}\n" +
                                f"Age: {data[row].get('age', 'Unknown')}\n" +
                                f"Sex: {data[row].get('sex', 'Unknown')}")

        self.setup_beliefs_table(data, row)
        self.setup_goals_table(data, row)
        self.setup_attributes_table(data, row)
        self.setup_traits_table(data, row)
        self.setup_thoughts_table(data, row)
        self.setup_needs_table(game_data, data, row)
        self.common_setup()

    def common_setup(self):
        for table in [self.beliefsTable, self.goalsTable, self.attributesTable, self.traitsTable, self.thoughtsTable, self.needsTable]:

            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setDefaultAlignment(Qt.AlignLeft)
            table.verticalHeader().setVisible(False)
            table.setSelectionMode(QAbstractItemView.NoSelection)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.resizeColumnToContents(1)

    def setup_beliefs_table(self, data: list[dict], row: int):
        beliefs: dict = data[row].get('beliefs', {})

        self.beliefsTable.setRowCount(len(beliefs))
        self.beliefsTable.setColumnCount(2)

        for i, belief in enumerate(beliefs):
            name, value = belief[1], str(belief[2])
            self.beliefsTable.setItem(i, 0, QTableWidgetItem(name))
            self.beliefsTable.setItem(i, 1, QTableWidgetItem(value))

        self.beliefsTable.horizontalHeader()
        self.beliefsTable.resizeColumnToContents(1)

    def setup_goals_table(self, data: list[dict], row: int):
        goals: dict = data[row].get('goals', {})

        self.goalsTable.setRowCount(len(goals))
        self.goalsTable.setColumnCount(2)

        for i, goal in enumerate(goals):
            name, value = goal[0]['name'], str(goal[1])
            self.goalsTable.setItem(i, 0, QTableWidgetItem(name))
            self.goalsTable.setItem(i, 1, QTableWidgetItem(value))

    def setup_attributes_table(self, data: list[dict], row: int):

        attributes: dict = data[row].get('attributes', {})
        attributes = sorted(attributes.items(), key=lambda item: item[1]["id"])

        self.attributesTable.setRowCount(len(attributes))
        self.attributesTable.setColumnCount(2)

        for i, attribute in enumerate(attributes):
            name, value = attribute[1]['name'], attribute[1]['value']
            self.attributesTable.setItem(i, 0, QTableWidgetItem(name))
            self.attributesTable.setItem(i, 1, QTableWidgetItem(str(value)))

    def setup_traits_table(self, data: list[dict], row: int):
        traits: dict = data[row].get('traits', {})

        self.traitsTable.setRowCount(len(traits))
        self.traitsTable.setColumnCount(2)

        for i, trait in enumerate(traits):
            name, value = trait[1], trait[2]
            self.traitsTable.setItem(i, 0, QTableWidgetItem(name))
            self.traitsTable.setItem(i, 1, QTableWidgetItem(str(value)))

    def setup_thoughts_table(self, data: list[dict], row: int):

        thoughts: dict = data[row].get('thoughts', {})

        self.thoughtsTable.setRowCount(len(thoughts))

        for i, thought in enumerate(thoughts):
            text = f"felt {thought['emotion_type'].lower()} {thought['thought']}"
            self.thoughtsTable.setItem(i, 0, QTableWidgetItem(text))

    def setup_needs_table(self, game_data: dict, data: list[dict], row: int):
        needs: dict = data[row].get('needs', {})

        self.needsTable.setRowCount(len(needs))

         # convert the need ids to their names
        for i, need in enumerate(needs):
            id = need["id"]
            name = need = game_data["needs"][id]["name"]
            self.needsTable.setItem(i, 0, QTableWidgetItem(name))