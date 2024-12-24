from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt6.QtCore import Qt

buttonActiveStylesheet = "font-family: 'More Perfect DOS VGA'; font-size: 5pt; border :2px solid gold;"
buttonStylesheet = "font-family: 'More Perfect DOS VGA'; font-size: 5pt;"


class DwarfInfoTab(QtWidgets.QWidget):
    def __init__(self, game_data: dict, data: dict, parent=None):
        super().__init__(parent)
        uic.loadUi('app/dwarfassistant/dwarfinfotab.ui', self)

        info_text = (
            f"Name: {data.get('first_name', 'Unknown')} {data.get('last_name', '')}\n"
            f"Profession: {data.get('profession', {}).get('name', 'Unknown')}\n"
            f"Age: {data.get('age', 'Unknown')}\n"
            f"Sex: {data.get('sex', 'Unknown')}"
        )
        self.infoLabel.setText(info_text)

        self.setup_beliefs_table(data)
        self.setup_goals_table(data)
        self.setup_attributes_table(data)
        self.setup_traits_table(data)
        self.setup_thoughts_table(data)
        self.setup_needs_table(game_data, data)
        self.setup_labors_table(data)
        self.setup_skills_table(data)

        # common setup for all tables
        tables = [self.beliefsTable, self.goalsTable, self.attributesTable,
                  self.traitsTable, self.thoughtsTable, self.needsTable, self.laborsTable]

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
            (self.attributesButton, self.attributesButtonClicked),
            (self.beliefsGoalsButton, self.beliefsGoalsButtonClicked),
            (self.laborsButton, self.laborsButtonClicked),
            (self.skillsButton, self.skillsButtonClicked)
        ]

        for button, handler in buttons:
            button.clicked.connect(handler)

        # these are the active buttons at the start
        self.skillsButton.setStyleSheet(buttonActiveStylesheet)
        self.attributesButton.setStyleSheet(buttonActiveStylesheet)

    def setup_beliefs_table(self, data: dict):
        beliefs = data.get('beliefs', {})

        self.beliefsTable.setRowCount(len(beliefs))
        self.beliefsTable.setColumnCount(2)

        for i, belief in enumerate(beliefs):
            name, value = belief[1], str(belief[2])
            self.beliefsTable.setItem(i, 0, QTableWidgetItem(name))
            self.beliefsTable.setItem(i, 1, QTableWidgetItem(value))

        self.beliefsTable.horizontalHeader()
        self.beliefsTable.resizeColumnToContents(1)

    def setup_goals_table(self, data: list[dict]):
        goals: dict = data.get('goals', {})

        self.goalsTable.setRowCount(len(goals))
        self.goalsTable.setColumnCount(2)

        for i, goal in enumerate(goals):
            name, value = goal[0]['name'], str(goal[1])
            self.goalsTable.setItem(i, 0, QTableWidgetItem(name))
            self.goalsTable.setItem(i, 1, QTableWidgetItem(value))

    def setup_attributes_table(self, data: list[dict]):

        attributes: dict = data.get('attributes', {})
        attributes = sorted(attributes.items(), key=lambda item: item[1]["id"])

        attributes = [
            [a for a in attributes[0:9]],
            [a for a in attributes[9:18]],
        ]
        self.attributesTable.setRowCount(9)
        self.attributesTable.setColumnCount(4)
        self.attributesTable.setColumnWidth(0, 75)
        self.attributesTable.setColumnWidth(1, 25)
        self.attributesTable.setColumnWidth(2, 75)
        self.attributesTable.setColumnWidth(3, 25)

        for i, attribute in enumerate(attributes[0]):
            name, value = attribute[1]['name'], attribute[1]['value']
            self.attributesTable.setItem(i, 0, QTableWidgetItem(name))
            self.attributesTable.setItem(i, 1, QTableWidgetItem(str(value)))

        for i, attribute in enumerate(attributes[1]):
            name, value = attribute[1]['name'], attribute[1]['value']
            self.attributesTable.setItem(i, 2, QTableWidgetItem(name))
            self.attributesTable.setItem(i, 3, QTableWidgetItem(str(value)))

    def setup_traits_table(self, data: list[dict]):
        traits: dict = data.get('traits', {})

        self.traitsTable.setRowCount(len(traits))
        self.traitsTable.setColumnCount(2)

        for i, trait in enumerate(traits):
            name, value = trait[1], trait[2]
            self.traitsTable.setItem(i, 0, QTableWidgetItem(name))
            self.traitsTable.setItem(i, 1, QTableWidgetItem(str(value)))

    def setup_thoughts_table(self, data: list[dict]):

        thoughts: dict = data.get('thoughts', {})

        self.thoughtsTable.setRowCount(len(thoughts))

        for i, thought in enumerate(thoughts):
            text = f"felt {thought['emotion_type'].lower()} {thought['thought']}"
            self.thoughtsTable.setItem(i, 0, QTableWidgetItem(text))

    def setup_needs_table(self, game_data: dict, data: list[dict]):
        needs: dict = data.get('needs', {})

        self.needsTable.setRowCount(len(needs))

         # convert the need ids to their names
        for i, need in enumerate(needs):
            id = need["id"]
            name = need = game_data["needs"][id]["name"]
            self.needsTable.setItem(i, 0, QTableWidgetItem(name))

    def setup_labors_table(self, data: list[dict]):
        labors: dict = data.get('labors', {})

        # sort the labors by enabled and then by id
        labors = sorted(labors.items(), key=lambda item: (not item[1]["enabled"], item[1]["id"]))


        self.laborsTable.setRowCount(len(labors))
        self.laborsTable.setColumnCount(2)

        for i, labor in enumerate(labors):
            self.laborsTable.setItem(i, 0, QTableWidgetItem(labor[1]["name"]))
            self.laborsTable.setItem(i, 1, QTableWidgetItem(str(labor[1]["enabled"])))

    def setup_skills_table(self, data: list[dict]):
        skills: dict = data.get('skills', {})
        # if the dwarf doesn't have 15 skills, fill the rest of the table with empty rows
        rows = len(skills) if len(skills) > 14 else 14
        self.skillsTable.setRowCount(rows)
        self.skillsTable.setColumnCount(2)

        for i, skill in enumerate(skills):
            self.skillsTable.setItem(i, 0, QTableWidgetItem(skill["name"]))
            self.skillsTable.setItem(i, 1, QTableWidgetItem(str(skill["raw_level"])))

        # Adjust the column widths
        # TODO: the column widths still suck
        self.skillsTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header = self.skillsTable.horizontalHeader()
        header.resizeSection(1, 25)

    def laborsButtonClicked(self):
        self.skillStack.setCurrentIndex(0)
        self.skillsButton.setStyleSheet(buttonStylesheet)
        self.laborsButton.setStyleSheet(buttonActiveStylesheet)

    def skillsButtonClicked(self):
        self.skillStack.setCurrentIndex(1)
        self.laborsButton.setStyleSheet(buttonStylesheet)
        self.skillsButton.setStyleSheet(buttonActiveStylesheet)

    def attributesButtonClicked(self):
        self.attributeStack.setCurrentIndex(0)
        self.beliefsGoalsButton.setStyleSheet(buttonStylesheet)
        self.attributesButton.setStyleSheet(buttonActiveStylesheet)

    def beliefsGoalsButtonClicked(self):
        self.attributeStack.setCurrentIndex(1)
        self.attributesButton.setStyleSheet(buttonStylesheet)
        self.beliefsGoalsButton.setStyleSheet(buttonActiveStylesheet)