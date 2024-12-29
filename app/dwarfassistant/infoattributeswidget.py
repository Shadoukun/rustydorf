from PyQt6 import QtCore, QtGui, QtWidgets

class InfoAttributesWidget(QtWidgets.QWidget):
    """This widget wraps the Dwarf Info label and the Attributes/Goals/Beliefs StackedWidget.

       I was having issues with the layout of the QLabel and the QStackedWidget, so I wrapped them in a QWidget
    """
    def __init__(self, parent=None):
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

        font = QtGui.QFont()
        font.setFamily("More Perfect DOS VGA")
        font.setPointSize(6)
        self.setFont(font)

        self.infoLabel = QtWidgets.QLabel("Info", self)
        self.infoLabel.setText((
            "Name: Test\n"
            "Profession: Miner\n"
            "Age: 88\n"
            "Sex: Male\n"
        ))

        self.infoLabel.setObjectName("infoLabel")
        self.infoLabel.setMaximumHeight(100)
        self.gridLayout.addWidget(self.infoLabel, 0, 0, 1, 1)

        # I hate Qt
        # create a horizontal layout for the buttons
        # can I scope this? Rust i miss you
        buttonWidget = QtWidgets.QWidget(self)
        buttonlayout = QtWidgets.QHBoxLayout(buttonWidget)
        buttonlayout.setContentsMargins(0, 0, 0, 0)
        buttonWidget.setLayout(buttonlayout)
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
        self.gridLayout.addWidget(self.attributeStack, 2, 0, 1, 3)

        ## Attributes Table (Page 1)
        page_1 = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page_1)
        layout.setContentsMargins(0, 0, 0, 0)
        self.attributesTable = QtWidgets.QTableWidget()
        self.attributesTable.setObjectName("attributesTable")
        self.attributesTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.attributesTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.attributesTable.setFont(font)

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
        self.beliefsTable.setFont(font)

        current_style = self.beliefsTable.styleSheet()
        self.beliefsTable.setStyleSheet(current_style + "QTableWidget {background: black;}")
        layout.addWidget(self.beliefsTable)

        self.goalsTable = QtWidgets.QTableWidget()
        self.goalsTable.setObjectName("goalsTable")
        self.goalsTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.goalsTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.goalsTable.setFont(font)

        current_style = self.goalsTable.styleSheet()
        self.goalsTable.setStyleSheet(current_style + "QTableWidget {background: black;}")
        layout.addWidget(self.goalsTable)

        self.attributeStack.addWidget(page_2)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = InfoAttributesWidget()
    window.show()
    sys.exit(app.exec())