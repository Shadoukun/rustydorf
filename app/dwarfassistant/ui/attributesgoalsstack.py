from PyQt6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout
from PyQt6 import QtCore, QtWidgets, QtGui

class AttributesGoalsStack(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("attributesGoalsStack")
        layout = QVBoxLayout()
        self.setLayout(layout)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setSizePolicy(sizePolicy)
        self.setMaximumWidth(150)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.attributesButton = QtWidgets.QPushButton(parent=self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.attributesButton.sizePolicy().hasHeightForWidth())
        self.attributesButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("More Perfect DOS VGA")
        font.setPointSize(6)
        self.attributesButton.setFont(font)
        self.attributesButton.setObjectName("attributesButton")
        self.gridLayout.addWidget(self.attributesButton, 0, 0, 1, 1)

        self.attributeStack = QtWidgets.QStackedWidget(parent=self)
        self.attributeStack.setObjectName("attributeStack")
        self.gridLayout.addWidget(self.attributeStack, 1, 0, 1, 3)

        self.beliefsGoalsButton = QtWidgets.QPushButton(parent=self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.beliefsGoalsButton.sizePolicy().hasHeightForWidth())
        self.beliefsGoalsButton.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setFamily("More Perfect DOS VGA")
        font.setPointSize(5)
        self.beliefsGoalsButton.setFont(font)
        self.beliefsGoalsButton.setObjectName("beliefsGoalsButton")
        self.gridLayout.addWidget(self.beliefsGoalsButton, 0, 1, 1, 1)
        self.attributeStack.setCurrentIndex(0)


class AttributesGoalsStackUI(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.widget = QtWidgets.QWidget(parent=Form)
        self.widget.setGeometry(QtCore.QRect(15, 10, 196, 196))
        self.widget.setObjectName("widget")

        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.attributesButton = QtWidgets.QPushButton(parent=self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.attributesButton.sizePolicy().hasHeightForWidth())
        self.attributesButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("More Perfect DOS VGA")
        font.setPointSize(6)
        self.attributesButton.setFont(font)
        self.attributesButton.setObjectName("attributesButton")
        self.attributesButton.setText("Attributes")
        self.gridLayout.addWidget(self.attributesButton, 0, 0, 1, 1)

        self.attributeStack = QtWidgets.QStackedWidget(parent=self.widget)
        self.attributeStack.setObjectName("attributeStack")
        self.gridLayout.addWidget(self.attributeStack, 1, 0, 1, 3)

        self.beliefsGoalsButton = QtWidgets.QPushButton(parent=self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.beliefsGoalsButton.sizePolicy().hasHeightForWidth())
        self.beliefsGoalsButton.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setFamily("More Perfect DOS VGA")
        font.setPointSize(5)
        self.beliefsGoalsButton.setFont(font)
        self.beliefsGoalsButton.setObjectName("beliefsGoalsButton")
        self.beliefsGoalsButton.setText("Beliefs/Goals")
        self.gridLayout.addWidget(self.beliefsGoalsButton, 0, 1, 1, 1)

        self.attributeStack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = AttributesGoalsStackUI()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())