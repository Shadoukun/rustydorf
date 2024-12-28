from PyQt6 import QtWidgets, uic, QtGui, QtCore
from PyQt6.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt6.QtCore import Qt

from .ui.dwarfinfotabui import DwarfInfoTabUI

buttonActiveStylesheet = "font-family: 'More Perfect DOS VGA'; font-size: 5pt; border :2px solid gold;"
buttonStylesheet = "font-family: 'More Perfect DOS VGA'; font-size: 5pt;"


class DwarfInfoTab(QtWidgets.QWidget):
    def __init__(self, game_data: dict, data: dict, parent=None):
        super().__init__(parent)
        self.ui = DwarfInfoTabUI()
        self.ui.setupUi(self)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        info_text = (
            f"Name: {data.get('first_name', 'Unknown')} {data.get('last_name', '')}\n"
            f"Profession: {data.get('profession', {}).get('name', 'Unknown')}\n"
            f"Age: {data.get('age', 'Unknown')}\n"
            f"Sex: {data.get('sex', 'Unknown')}"
        )
        self.ui.infoLabel.setText(info_text)
        self.layout.addWidget(self.ui.infoLabel)
        self.layout.addWidget(self.ui.attributesStack)
        # self.setup_beliefs_table(data)
        # self.setup_goals_table(data)
        # self.setup_attributes_table(data)
        self.setup_traits_table(data)
        self.setup_thoughts_table(data)
        self.setup_needs_table(game_data, data)
        self.setup_labors_table(data)
        self.setup_skills_table(data)

        # common setup for all tables
        tables = [self.ui.traitsTable, self.ui.thoughtsTable, self.ui.needsTable, self.ui.laborsTable]

        for table in tables:
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
            table.verticalHeader().setVisible(False)
            table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.resizeColumnToContents(1)

        # setup the buttons
        buttons = [
            (self.ui.laborsButton, self.laborsButtonClicked),
            (self.ui.skillsButton, self.skillsButtonClicked)
        ]

        for button, handler in buttons:
            button.clicked.connect(handler)

        # these are the active buttons at the start
        self.ui.skillsButton.setStyleSheet(buttonActiveStylesheet)

    def setup_beliefs_table(self, data: dict):
        beliefs = data.get('beliefs', {})

        self.ui.beliefsTable.setRowCount(len(beliefs))
        self.ui.beliefsTable.setColumnCount(2)

        for i, belief in enumerate(beliefs):
            name, value = belief[1], str(belief[2])
            self.ui.beliefsTable.setItem(i, 0, QTableWidgetItem(name))
            self.ui.beliefsTable.setItem(i, 1, QTableWidgetItem(value))

        self.ui.beliefsTable.horizontalHeader()
        self.ui.beliefsTable.resizeColumnToContents(1)

    def setup_goals_table(self, data: list[dict]):
        goals: dict = data.get('goals', {})

        self.ui.goalsTable.setRowCount(len(goals))
        self.ui.goalsTable.setColumnCount(2)

        for i, goal in enumerate(goals):
            name, value = goal[0]['name'], str(goal[1])
            self.ui.goalsTable.setItem(i, 0, QTableWidgetItem(name))
            self.ui.goalsTable.setItem(i, 1, QTableWidgetItem(value))

    def setup_attributes_table(self, data: list[dict]):

        attributes: dict = data.get('attributes', {})
        attributes = sorted(attributes.items(), key=lambda item: item[1]["id"])

        attributes = [
            [a for a in attributes[0:9]],
            [a for a in attributes[9:18]],
        ]
        self.ui.attributesTable.setRowCount(9)
        self.ui.attributesTable.setColumnCount(4)
        self.ui.attributesTable.setColumnWidth(0, 75)
        self.ui.attributesTable.setColumnWidth(1, 25)
        self.ui.attributesTable.setColumnWidth(2, 75)
        self.ui.attributesTable.setColumnWidth(3, 25)

        for i, attribute in enumerate(attributes[0]):
            name, value = attribute[1]['name'], attribute[1]['value']
            self.ui.attributesTable.setItem(i, 0, QTableWidgetItem(name))
            self.ui.attributesTable.setItem(i, 1, QTableWidgetItem(str(value)))

        for i, attribute in enumerate(attributes[1]):
            name, value = attribute[1]['name'], attribute[1]['value']
            self.ui.attributesTable.setItem(i, 2, QTableWidgetItem(name))
            self.ui.attributesTable.setItem(i, 3, QTableWidgetItem(str(value)))

    def setup_traits_table(self, data: list[dict]):
        traits: dict = data.get('traits', {})

        self.ui.traitsTable.setRowCount(len(traits))
        self.ui.traitsTable.setColumnCount(2)

        for i, trait in enumerate(traits):
            name, value = trait[1], trait[2]
            self.ui.traitsTable.setItem(i, 0, QTableWidgetItem(name))
            self.ui.traitsTable.setItem(i, 1, QTableWidgetItem(str(value)))

    def setup_thoughts_table(self, data: list[dict]):

        thoughts: dict = data.get('thoughts', {})

        self.ui.thoughtsTable.setRowCount(len(thoughts))

        for i, thought in enumerate(thoughts):
            text = f"felt {thought['emotion_type'].lower()} {thought['thought']}"
            self.ui.thoughtsTable.setItem(i, 0, QTableWidgetItem(text))

    def setup_needs_table(self, game_data: dict, data: list[dict]):
        needs: dict = data.get('needs', {})

        self.ui.needsTable.setRowCount(len(needs))

         # convert the need ids to their names
        for i, need in enumerate(needs):
            id = need["id"]
            name = need = game_data["needs"][id]["name"]
            self.ui.needsTable.setItem(i, 0, QTableWidgetItem(name))

    def setup_labors_table(self, data: list[dict]):
        labors: dict = data.get('labors', {})

        # sort the labors by enabled and then by id
        labors = sorted(labors.items(), key=lambda item: (not item[1]["enabled"], item[1]["id"]))


        self.ui.laborsTable.setRowCount(len(labors))
        self.ui.laborsTable.setColumnCount(2)

        for i, labor in enumerate(labors):
            self.ui.laborsTable.setItem(i, 0, QTableWidgetItem(labor[1]["name"]))
            self.ui.laborsTable.setItem(i, 1, QTableWidgetItem(str(labor[1]["enabled"])))

    def setup_skills_table(self, data: list[dict]):
        skills: dict = data.get('skills', {})
        # if the dwarf doesn't have 15 skills, fill the rest of the table with empty rows
        rows = len(skills) if len(skills) > 14 else 14
        self.ui.skillsTable.setRowCount(rows)
        self.ui.skillsTable.setColumnCount(2)

        for i, skill in enumerate(skills):
            self.ui.skillsTable.setItem(i, 0, QTableWidgetItem(skill["name"]))
            self.ui.skillsTable.setItem(i, 1, QTableWidgetItem(str(skill["raw_level"])))

        # Adjust the column widths
        # TODO: the column widths still suck
        self.ui.skillsTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header = self.ui.skillsTable.horizontalHeader()
        header.resizeSection(1, 25)

    def laborsButtonClicked(self):
        self.ui.skillStack.setCurrentIndex(0)
        self.ui.skillsButton.setStyleSheet(buttonStylesheet)
        self.ui.laborsButton.setStyleSheet(buttonActiveStylesheet)

    def skillsButtonClicked(self):
        self.ui.skillStack.setCurrentIndex(1)
        self.ui.laborsButton.setStyleSheet(buttonStylesheet)
        self.ui.skillsButton.setStyleSheet(buttonActiveStylesheet)

    def attributesButtonClicked(self):
        self.ui.attributeStack.setCurrentIndex(0)
        self.ui.beliefsGoalsButton.setStyleSheet(buttonStylesheet)
        self.ui.attributesButton.setStyleSheet(buttonActiveStylesheet)

    def beliefsGoalsButtonClicked(self):
        self.ui.attributeStack.setCurrentIndex(1)
        self.ui.attributesButton.setStyleSheet(buttonStylesheet)
        self.ui.beliefsGoalsButton.setStyleSheet(buttonActiveStylesheet)
