from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import QSettings

class InfoAttributesWidget(QtWidgets.QWidget):
    """This widget wraps the Dwarf Info label and the Attributes/Goals/Beliefs StackedWidget.

       I was having issues with the layout of the QLabel and the QStackedWidget, so I wrapped them in a QWidget
    """
    def __init__(self, parent=None, data: dict = None, settings: QSettings = None):
        super().__init__(parent)
        sizepolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizepolicy.setHorizontalStretch(0)
        sizepolicy.setVerticalStretch(0)
        self.setSizePolicy(sizepolicy)
        self.setMinimumHeight(50)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gridLayout)

        # Info Label
        self.infoLabel = QtWidgets.QLabel("Info", self)
        self.infoLabel.setObjectName("infoLabel")
        self.infoLabel.setMaximumHeight(300)
        sizepolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizepolicy.setHorizontalStretch(0)
        sizepolicy.setVerticalStretch(0)
        self.infoLabel.setSizePolicy(sizepolicy)
        self.infoLabel.setText((
            f"Name: {data.get('first_name', 'Unknown')} {data.get('last_name', '')}\n"
            f"Profession: {data.get('profession', {}).get('name', 'Unknown')}\n"
            f"Age: {data.get('age', 'Unknown')}\n"
            f"Sex: {data.get('sex', 'Unknown')}"
        ))
        self.gridLayout.addWidget(self.infoLabel, 0, 0, 1, 1)

        # I hate Qt
        # create a horizontal layout for the buttons
        buttonWidget = QtWidgets.QWidget(self)
        buttonlayout = QtWidgets.QHBoxLayout(buttonWidget)
        buttonWidget.setLayout(buttonlayout)
        buttonlayout.setContentsMargins(0, 10, 0, 5)

        self.gridLayout.addWidget(buttonWidget, 1, 0, 1, 2)

        # Attributes Button
        self.attributesButton = QtWidgets.QPushButton(self)
        btnSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.attributesButton.setSizePolicy(btnSizePolicy)
        self.attributesButton.setFont(QtGui.QFont("More Perfect DOS VGA", 6))
        self.attributesButton.setText("Attributes")
        buttonlayout.addWidget(self.attributesButton)

        # Beliefs/Goals Button
        self.beliefsGoalsButton = QtWidgets.QPushButton(self)
        self.beliefsGoalsButton.setSizePolicy(btnSizePolicy)
        self.beliefsGoalsButton.setFont(QtGui.QFont("More Perfect DOS VGA", 6))
        self.beliefsGoalsButton.setText("Beliefs/Goals")
        buttonlayout.addWidget(self.beliefsGoalsButton)

        # Button spacer
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)

        # Stacked Widget
        self.attributeStack = QtWidgets.QStackedWidget(self)
        self.attributeStack.setObjectName("attributeStack")
        self.attributeStack.setMaximumHeight(250)
        self.attributeStack.setMaximumWidth(400)
        self.setMinimumWidth(200)
        self.gridLayout.addWidget(self.attributeStack, 2, 0, 1, 3)

        ## Attributes Table (Page 1)
        page_1 = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page_1)
        layout.setContentsMargins(0, 0, 0, 0)
        self.attributesTable = QtWidgets.QTableWidget()
        self.attributesTable.setObjectName("attributesTable")
        self.attributesTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.attributesTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)

        current_style = self.attributesTable.styleSheet()
        # TODO: figure out why when using setStyleSheet, it negates changing the height of the rows with SetDefaultSectionSize
        self.attributesTable.setStyleSheet(current_style + "QTableWidget {background: black;}")
        layout.addWidget(self.attributesTable)
        self.attributeStack.addWidget(page_1)

        ## Beliefs/Goals Table (Page 2)
        page_2 = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(page_2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.beliefsTable = QtWidgets.QTableWidget()
        self.beliefsTable.setObjectName("beliefsGoalsTable")
        self.beliefsTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.beliefsTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)

        current_style = self.beliefsTable.styleSheet()
        self.beliefsTable.setStyleSheet(current_style + "QTableWidget {background: black;}")
        layout.addWidget(self.beliefsTable)

        self.goalsTable = QtWidgets.QTableWidget()
        self.goalsTable.setObjectName("goalsTable")
        self.goalsTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.goalsTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)

        current_style = self.goalsTable.styleSheet()
        self.goalsTable.setStyleSheet(current_style + "QTableWidget {background: black;}")
        layout.addWidget(self.goalsTable)

        self.attributeStack.addWidget(page_2)

        # fonts are awful
        font_name = settings.value("font_name", "More Perfect DOS VGA", type=str)
        font_size = settings.value("font_size", 6, type=int)
        font = QtGui.QFont(font_name, font_size)

        for t in [self.attributesTable, self.beliefsTable, self.goalsTable]:
            t.setFont(font)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = InfoAttributesWidget()
    window.show()
    sys.exit(app.exec())