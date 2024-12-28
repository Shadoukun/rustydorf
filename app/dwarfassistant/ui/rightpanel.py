
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget

class RightPanelWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("rightPanel")
        self.setMaximumWidth(151)

        # Grid Layout
        self.gridlayout = QtWidgets.QGridLayout(self)
        self.gridlayout.setObjectName("gridLayout")
        self.gridlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gridlayout)

        # Button Widget
        self.buttonWidget = QtWidgets.QWidget(self)
        buttonlayout = QtWidgets.QHBoxLayout(self.buttonWidget)
        buttonlayout.setContentsMargins(0, 0, 0, 0)
        self.buttonWidget.setLayout(buttonlayout)
        self.gridlayout.addWidget(self.buttonWidget, 0, 0, 1, 2)

        ## Skills Button
        self.skillsButton = QtWidgets.QPushButton(self) # Attributes Button
        btnSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.skillsButton.setSizePolicy(btnSizePolicy)
        self.skillsButton.setFont(QtGui.QFont("More Perfect DOS VGA", 6))
        self.skillsButton.setText("Skills")
        buttonlayout.addWidget(self.skillsButton)

        ## Labors Button
        self.laborsButton = QtWidgets.QPushButton(self) # Beliefs/Goals Button
        self.laborsButton.setSizePolicy(btnSizePolicy)
        self.laborsButton.setFont(QtGui.QFont("More Perfect DOS VGA", 6))
        self.laborsButton.setText("Labors")
        buttonlayout.addWidget(self.laborsButton)

        ## Button Spacer
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 2, 1, 1)

        # Stack Widget
        self.stackWidget = QtWidgets.QStackedWidget(parent=self)
        self.stackWidget.setObjectName("stackWidget")
        self.stackWidget.setMaximumWidth(150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackWidget.sizePolicy().hasHeightForWidth())
        self.stackWidget.setSizePolicy(sizePolicy)
        self.gridlayout.addWidget(self.stackWidget, 1, 0, 1, 3)

        ## Skills Page

        self.skillsPage = QtWidgets.QWidget()
        self.skillsPage.setObjectName("skillsPage")
        layout = QtWidgets.QVBoxLayout(self.skillsPage)
        layout.setContentsMargins(0, 0, 0, 0)
        self.skillsPage.setLayout(layout)
        self.stackWidget.addWidget(self.skillsPage)

        ### Skills Table

        self.skillsTable = QtWidgets.QTableWidget(parent=self.skillsPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.skillsTable.sizePolicy().hasHeightForWidth())
        self.skillsTable.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("More Perfect DOS VGA")
        self.skillsTable.setFont(font)
        self.skillsTable.setObjectName("skillsTable")
        self.skillsTable.setColumnCount(0)
        self.skillsTable.setRowCount(0)
        self.skillsTable.horizontalHeader().setVisible(False)
        self.skillsTable.horizontalHeader().setHighlightSections(False)
        self.skillsTable.verticalHeader().setVisible(False)
        self.skillsTable.verticalHeader().setHighlightSections(False)
        layout.addWidget(self.skillsTable)

        # self.stackWidget = QtWidgets.QStackedWidget(parent=self)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.stackWidget.sizePolicy().hasHeightForWidth())
        # self.stackWidget.setSizePolicy(sizePolicy)

        # self.page_1 = QtWidgets.QWidget()
        # self.page_1.setObjectName("page_1")

        # self.laborsTable = QtWidgets.QTableWidget(parent=self)
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.laborsTable.sizePolicy().hasHeightForWidth())
        # self.laborsTable.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setFamily("More Perfect DOS VGA")
        # self.laborsTable.setFont(font)
        # self.laborsTable.setObjectName("laborsTable")
        # self.laborsTable.setColumnCount(0)
        # self.laborsTable.setRowCount(0)
        # self.laborsTable.horizontalHeader().setVisible(False)
        # self.laborsTable.horizontalHeader().setHighlightSections(False)
        # self.laborsTable.verticalHeader().setVisible(False)
        # self.laborsTable.verticalHeader().setHighlightSections(False)
        # # self.stackWidget.addWidget(self.page_1)

        # layout.addWidget(self.laborsTable)
        # self.skillStack.setObjectName("skillStack")
        # self.page_3 = QtWidgets.QWidget()
        # self.page_3.setObjectName("page_3")

        # self.laborsTable = QtWidgets.QTableWidget(parent=self.page_3)
        # self.laborsTable.setGeometry(QtCore.QRect(0, 0, 151, 586))
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Expanding)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.laborsTable.sizePolicy().hasHeightForWidth())
        # self.laborsTable.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setFamily("More Perfect DOS VGA")
        # self.laborsTable.setFont(font)
        # self.laborsTable.setObjectName("laborsTable")
        # self.laborsTable.setColumnCount(0)
        # self.laborsTable.setRowCount(0)
        # self.laborsTable.horizontalHeader().setVisible(False)
        # self.laborsTable.horizontalHeader().setHighlightSections(False)
        # self.laborsTable.verticalHeader().setVisible(False)
        # self.laborsTable.verticalHeader().setHighlightSections(False)
        # self.skillStack.addWidget(self.page_3)
        # self.page_4 = QtWidgets.QWidget()
        # self.page_4.setObjectName("page_4")

        # self.skillsTable = QtWidgets.QTableWidget(parent=self.page_4)
        # self.skillsTable.setGeometry(QtCore.QRect(0, 0, 151, 441))
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Expanding)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.skillsTable.sizePolicy().hasHeightForWidth())
        # self.skillsTable.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setFamily("More Perfect DOS VGA")
        # self.skillsTable.setFont(font)
        # self.skillsTable.setObjectName("skillsTable")
        # self.skillsTable.setColumnCount(0)
        # self.skillsTable.setRowCount(0)
        # self.skillsTable.horizontalHeader().setVisible(False)
        # self.skillsTable.horizontalHeader().setHighlightSections(False)
        # self.skillsTable.verticalHeader().setVisible(False)
        # self.skillsTable.verticalHeader().setHighlightSections(False)
        # self.skillStack.addWidget(self.page_4)
        # self.skillsButton = QtWidgets.QPushButton(parent=Form)
        # self.skillsButton.setGeometry(QtCore.QRect(470, 10, 41, 21))
        # font = QtGui.QFont()
        # font.setFamily("More Perfect DOS VGA")
        # font.setPointSize(6)
        # self.skillsButton.setFont(font)
        # self.skillsButton.setObjectName("skillsButton")

        # self.laborsButton = QtWidgets.QPushButton(parent=Form)
        # self.laborsButton.setGeometry(QtCore.QRect(515, 10, 41, 21))
        # font = QtGui.QFont()
        # font.setFamily("More Perfect DOS VGA")
        # font.setPointSize(6)
        # self.laborsButton.setFont(font)
        # self.laborsButton.setObjectName("laborsButton")

        # self.skillStack.setCurrentIndex(1)
        # QtCore.QMetaObject.connectSlotsByName(Form)