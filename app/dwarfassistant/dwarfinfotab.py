from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt6.QtCore import Qt, QSettings

from .infoattributeswidget import InfoAttributesWidget
from .rightpanel import RightPanelWidget
from .components.progresstablecell import ProgressTableCell

buttonActiveStylesheet = "border :2px solid gold;"
buttonStylesheet = ""


class DwarfInfoTab(QtWidgets.QWidget):
    """
    This is the top level widget for the dwarf info panel on the right side of the main window.

    It creates the main widget and the right panel widget and contains the logic for initializing them.
    """

    def __init__(self, parent, game_data: dict, data: dict, settings: QSettings):
        super().__init__(parent)
        self.settings = settings
        self.setObjectName("mainPanel")

        # for some reason the font size is not being set by the parent widget
        font = self.get_font()
        self.setFont(font)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        # Splitter
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setObjectName("splitter")

        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        layout.addWidget(self.splitter)

        # Main Panel

        self.mainPanel = QtWidgets.QWidget(self)
        self.mainPanel.setObjectName("mainPanel")
        mainPanelLayout = QtWidgets.QGridLayout(self.mainPanel)
        mainPanelLayout.setObjectName("mainpanelLayout")
        self.mainPanel.setLayout(mainPanelLayout)
        self.splitter.addWidget(self.mainPanel)

        ## Info / Attributes Widget

        self.infoAttributesWidget = InfoAttributesWidget(self, data, settings)
        self.infoAttributesWidget.setObjectName("infoWidget")
        self.infoAttributesWidget.setFont(font)
        mainPanelLayout.addWidget(self.infoAttributesWidget, 0, 0, 1, 1)

        ## Needs Table

        self.needsTable = QtWidgets.QTableWidget(parent=self)
        self.needsTable.setObjectName("needsTable")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        self.needsTable.setMinimumWidth(100)
        self.needsTable.setMaximumWidth(500)
        self.needsTable.setSizePolicy(sizePolicy)
        self.needsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.needsTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.needsTable.setSizePolicy(sizePolicy)
        self.needsTable.setColumnCount(1)
        self.needsTable.setRowCount(0)
        self.needsTable.setFont(font)
        item = QtWidgets.QTableWidgetItem()
        self.needsTable.setHorizontalHeaderItem(0, item)
        self.needsTable.horizontalHeader().setStretchLastSection(True)
        mainPanelLayout.addWidget(self.needsTable, 0, 1, 1, 1)

        ## Thoughts Table

        self.thoughtsTable = QtWidgets.QTableWidget(parent=self)
        self.thoughtsTable.setObjectName("thoughtsTable")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thoughtsTable.sizePolicy().hasHeightForWidth())
        self.thoughtsTable.setSizePolicy(sizePolicy)
        self.thoughtsTable.setColumnCount(1)
        self.thoughtsTable.setRowCount(0)
        self.thoughtsTable.setFont(font)
        item = QtWidgets.QTableWidgetItem()
        self.thoughtsTable.setHorizontalHeaderItem(0, item)
        self.thoughtsTable.horizontalHeader().setStretchLastSection(True)
        mainPanelLayout.addWidget(self.thoughtsTable, 1, 0, 1, 2)

        # Right Panel Widget

        self.rightPanelWidget = RightPanelWidget(self, self.settings)
        self.rightPanelWidget.setObjectName("rightPanelWidget")
        self.splitter.addWidget(self.rightPanelWidget)

        # set the initial data for the tables
        # TODO: figure out why this errors if its at the end of __init__
        self.update_data(data, game_data, settings)

        # # common setup for all tables
        tables = [
            self.thoughtsTable, self.infoAttributesWidget.attributesTable,
            self.needsTable, self.rightPanelWidget.traitsTable,
            self.rightPanelWidget.skillsTable, self.infoAttributesWidget.beliefsTable,
            self.infoAttributesWidget.goalsTable
        ]

        for table in tables:
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
            header.setVisible(False)
            header = table.verticalHeader()
            header.setVisible(False)
            table.verticalHeader().setVisible(False)
            table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.resizeColumnToContents(1)

        # connect the buttons to their handlers
        buttons = [
            (self.rightPanelWidget.traitsButton, self.traitsButtonClicked),
            (self.rightPanelWidget.skillsButton, self.skillsButtonClicked),
            (self.infoAttributesWidget.attributesButton, self.attributesButtonClicked),
            (self.infoAttributesWidget.beliefsGoalsButton, self.beliefsGoalsButtonClicked),
        ]

        for button, handler in buttons:
            button.clicked.connect(handler)

        # these are the active buttons at the start
        self.infoAttributesWidget.attributesButton.setStyleSheet(buttonActiveStylesheet)
        self.rightPanelWidget.skillsButton.setStyleSheet(buttonActiveStylesheet)

        existing = self.styleSheet()
        self.setStyleSheet(existing + """ \
            QPushButton { \
                padding: 10px; \
            }""")

    def update_data(self, data: dict, game_data: dict, settings: QSettings):
        self.infoAttributesWidget.infoLabel.setText((
            f"Name: {data.get('first_name', 'Unknown')} {data.get('last_name', '')}\n"
            f"Profession: {data.get('profession', {}).get('name', 'Unknown')}\n"
            f"Age: {data.get('age', 'Unknown')}\n"
            f"Sex: {data.get('sex', 'Unknown')}"
        ))

        self.setup_beliefs_table(data)
        self.setup_goals_table(data)
        self.setup_attributes_table(data)
        self.setup_traits_table(data)
        self.setup_thoughts_table(data)
        self.setup_needs_table(game_data, data)
        self.setup_skills_table(data)

    def setup_beliefs_table(self, data: dict):
        beliefs = data.get('beliefs', {})

        self.infoAttributesWidget.beliefsTable.setRowCount(len(beliefs))
        self.infoAttributesWidget.beliefsTable.setColumnCount(2)

        for i, belief in enumerate(beliefs):
            name, value = belief[1], str(belief[2])
            self.infoAttributesWidget.beliefsTable.setItem(i, 0, QTableWidgetItem(name))
            self.infoAttributesWidget.beliefsTable.setItem(i, 1, QTableWidgetItem(value))

        self.infoAttributesWidget.beliefsTable.horizontalHeader()
        self.infoAttributesWidget.beliefsTable.resizeColumnToContents(1)

    def setup_goals_table(self, data: list[dict]):
        goals: dict = data.get('goals', {})

        self.infoAttributesWidget.goalsTable.setRowCount(len(goals))
        self.infoAttributesWidget.goalsTable.setColumnCount(2)

        for i, goal in enumerate(goals):
            name, value = goal[0]['name'], str(goal[1])
            self.infoAttributesWidget.goalsTable.setItem(i, 0, QTableWidgetItem(name))
            self.infoAttributesWidget.goalsTable.setItem(i, 1, QTableWidgetItem(value))

    def setup_attributes_table(self, data: list[dict]):

        attributes: dict = data.get('attributes', {})
        attributes = sorted(attributes.items(), key=lambda item: item[1]["id"])

        attributes = [
            [a for a in attributes[0:9]],
            [a for a in attributes[9:18]],
        ]

        table = self.infoAttributesWidget.attributesTable
        table.setRowCount(9)
        table.setColumnCount(4)
        table.setColumnWidth(0, 75)
        table.setColumnWidth(1, 25)
        table.setColumnWidth(2, 75)
        table.setColumnWidth(3, 25)

        header = self.infoAttributesWidget.attributesTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setVisible(False)
        table.verticalHeader().setDefaultSectionSize(20)

        for i, attribute in enumerate(attributes[0]):
            name, value = attribute[1]['name'], attribute[1]['value']
            self.infoAttributesWidget.attributesTable.setItem(i, 0, QTableWidgetItem(name))
            self.infoAttributesWidget.attributesTable.setItem(i, 1, QTableWidgetItem(str(value)))

        for i, attribute in enumerate(attributes[1]):
            name, value = attribute[1]['name'], attribute[1]['value']
            self.infoAttributesWidget.attributesTable.setItem(i, 2, QTableWidgetItem(name))
            self.infoAttributesWidget.attributesTable.setItem(i, 3, QTableWidgetItem(str(value)))

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

    def setup_skills_table(self, data: list[dict]):
        skills: dict = data.get('skills', {})
        skills = sorted(skills, key=lambda item: item["raw_level"], reverse=True)

        # if the dwarf doesn't have 15 skills, fill the rest of the table with empty rows
        rows = len(skills) if len(skills) > 14 else 14
        self.rightPanelWidget.skillsTable.setRowCount(rows)
        self.rightPanelWidget.skillsTable.setColumnCount(1)

        for i, skill in enumerate(skills):
            widget = ProgressTableCell(self)
            widget.nameLabel.setText(skill["name"])
            widget.valueLabel.setText(str(skill["raw_level"]))

            widget.progress.setRange(0, 15)
            widget.progress.setValue(skill["raw_level"])
            self.rightPanelWidget.skillsTable.setCellWidget(i, 0, widget)

        self.rightPanelWidget.skillsTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header = self.rightPanelWidget.skillsTable.horizontalHeader()
        header.resizeSection(1, 25)

    def setup_traits_table(self, data: list[dict]):
        traits: dict = data.get('traits', {})

        self.rightPanelWidget.traitsTable.setRowCount(len(traits))
        self.rightPanelWidget.traitsTable.setColumnCount(1)

        for i, trait in enumerate(traits):
            widget = ProgressTableCell(self)
            widget.progress.setRange(0, 255)
            widget.nameLabel.setText(trait[1])
            widget.valueLabel.setText(str(trait[2]))
            widget.progress.setValue(trait[2])
            self.rightPanelWidget.traitsTable.setCellWidget(i, 0, widget)


    def get_font(self):
        font_name = self.settings.value("font_name", "More Perfect DOS VGA", type=str)
        font_size = self.settings.value("font_size", 6, type=int)
        return QtGui.QFont(font_name, font_size)

    def skillsButtonClicked(self):
        self.rightPanelWidget.stackWidget.setCurrentIndex(0)
        self.rightPanelWidget.traitsButton.setStyleSheet(buttonStylesheet)
        self.rightPanelWidget.skillsButton.setStyleSheet(buttonActiveStylesheet)

    def traitsButtonClicked(self):
        self.rightPanelWidget.stackWidget.setCurrentIndex(1)
        self.rightPanelWidget.skillsButton.setStyleSheet(buttonStylesheet)
        self.rightPanelWidget.traitsButton.setStyleSheet(buttonActiveStylesheet)

    def attributesButtonClicked(self):
        font = self.get_font()
        self.infoAttributesWidget.attributeStack.setCurrentIndex(0)
        self.infoAttributesWidget.beliefsGoalsButton.setStyleSheet(buttonStylesheet)
        self.infoAttributesWidget.beliefsGoalsButton.setFont(font)
        self.infoAttributesWidget.attributesButton.setStyleSheet(buttonActiveStylesheet)
        self.infoAttributesWidget.attributesButton.setFont(font)

    def beliefsGoalsButtonClicked(self):
        font = self.get_font()
        self.infoAttributesWidget.attributeStack.setCurrentIndex(1)
        self.infoAttributesWidget.attributesButton.setStyleSheet(buttonStylesheet)
        self.infoAttributesWidget.attributesButton.setFont(font)
        self.infoAttributesWidget.beliefsGoalsButton.setStyleSheet(buttonActiveStylesheet)
        self.infoAttributesWidget.beliefsGoalsButton.setFont(font)
