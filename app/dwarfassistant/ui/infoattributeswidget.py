from PyQt6 import QtCore, QtGui, QtWidgets

class InfoAttributesWidget(QtWidgets.QWidget):
    """This widget wraps the Dwarf Info label and the Attributes/Goals/Beliefs StackedWidget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        sizepolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizepolicy.setHorizontalStretch(0)
        sizepolicy.setVerticalStretch(0)
        self.setSizePolicy(sizepolicy)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

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
        layout.addWidget(self.infoLabel)

        self.attributeStack = AttributesGoalsStack(self)
        self.attributeStack.setObjectName("attributeStack")
        layout.addWidget(self.attributeStack)
        self.setLayout(layout)


class AttributesGoalsStack(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AttributesGoalsStack")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setFamily("More Perfect DOS VGA")
        font.setPointSize(6)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        # Attributes Button
        self.attributesButton = QtWidgets.QPushButton(self)
        btnSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.attributesButton.setSizePolicy(btnSizePolicy)
        self.attributesButton.setFont(QtGui.QFont("More Perfect DOS VGA", 6))
        self.attributesButton.setText("Attributes")
        self.gridLayout.addWidget(self.attributesButton, 0, 0, 1, 1)

        # Beliefs/Goals Button
        self.beliefsGoalsButton = QtWidgets.QPushButton(self)
        self.beliefsGoalsButton.setSizePolicy(btnSizePolicy)
        self.beliefsGoalsButton.setFont(QtGui.QFont("More Perfect DOS VGA", 6))
        self.beliefsGoalsButton.setText("Beliefs/Goals")
        self.gridLayout.addWidget(self.beliefsGoalsButton, 0, 1, 1, 1)

        # Stacked Widget
        self.attributeStack = QtWidgets.QStackedWidget(self)

        page_1 = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page_1)
        self.attributesTable = QtWidgets.QTableWidget()
        self.attributesTable.setObjectName("attributesTable")
        self.attributesTable.setMinimumHeight(200)
        self.attributesTable.setMaximumHeight(250)
        current_style = self.attributesTable.styleSheet()
        # TODO: figure out why when using setStyleSheet, it negates changing the height of the rows with SetDefaultSectionSize
        self.attributesTable.setStyleSheet(current_style + "QTableWidget {background: black;}")

        self.attributesTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.attributesTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.attributesTable.setFont(font)
        layout.addWidget(self.attributesTable)
        self.attributeStack.addWidget(page_1)
        self.gridLayout.addWidget(self.attributeStack, 1, 0, 1, 3)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)

        self.attributeStack.setCurrentIndex(0)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = InfoAttributesWidget()
    window.show()
    sys.exit(app.exec())