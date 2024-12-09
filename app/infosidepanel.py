from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6 import QtCore, QtGui, QtWidgets


class SidePanelWidget(QWidget):
    def __init__(self, parent=None):
        super(SidePanelWidget, self).__init__(parent)
        self.setupUi(self)

    def setupUi(self, Widget):
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(10)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addStretch()  # Pushes buttons to the right

        font = QtGui.QFont()
        font.setFamily("More Perfect DOS VGA")

        self.skillsButton = QtWidgets.QPushButton(parent=self)
        self.skillsButton.setMinimumSize(QtCore.QSize(41, 31))
        self.skillsButton.setFont(font)
        self.buttonLayout.addWidget(self.skillsButton)

        self.laborsButton = QtWidgets.QPushButton(parent=self)
        self.laborsButton.setMinimumSize(QtCore.QSize(41, 31))
        self.laborsButton.setFont(font)
        self.buttonLayout.addWidget(self.laborsButton)

        self.verticalLayout.addLayout(self.buttonLayout)

        self.stackedWidget = QtWidgets.QStackedWidget(parent=self)
        self.stackedWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addWidget(self.stackedWidget)

        self.page = QtWidgets.QWidget()
        self.tableWidget = QtWidgets.QTableWidget(parent=self.page)
        page_layout = QtWidgets.QVBoxLayout(self.page)
        page_layout.addWidget(self.tableWidget)
        self.stackedWidget.addWidget(self.page)

        self.page_2 = QtWidgets.QWidget()
        self.stackedWidget.addWidget(self.page_2)
