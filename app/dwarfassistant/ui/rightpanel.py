
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget

class RightPanelWidget(QtWidgets.QWidget):
    """This is the the right panel widget that contains the Skills and Labors tables."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("rightPanel")
        self.setMaximumWidth(151)
        font = QtGui.QFont()
        font.setFamily("More Perfect DOS VGA")
        font.setPointSize(6)

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
        self.skillsTable.setObjectName("skillsTable")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.skillsTable.sizePolicy().hasHeightForWidth())
        self.skillsTable.setSizePolicy(sizePolicy)
        self.skillsTable.setFont(font)
        self.skillsTable.setColumnCount(0)
        self.skillsTable.setRowCount(0)
        layout.addWidget(self.skillsTable)

        ## Labors Page

        self.laborsPage = QtWidgets.QWidget()
        self.laborsPage.setObjectName("laborsPage")
        layout = QtWidgets.QVBoxLayout(self.laborsPage)
        layout.setContentsMargins(0, 0, 0, 0)
        self.laborsPage.setLayout(layout)
        self.stackWidget.addWidget(self.laborsPage)

        ### Labors Table

        self.laborsTable = QtWidgets.QTableWidget(parent=self.laborsPage)
        self.laborsTable.setObjectName("laborsTable")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.laborsTable.sizePolicy().hasHeightForWidth())
        self.laborsTable.setSizePolicy(sizePolicy)
        self.laborsTable.setFont(font)
        self.laborsTable.setColumnCount(0)
        self.laborsTable.setRowCount(0)
        layout.addWidget(self.laborsTable)

        # Common Table Settings

        for t in [self.skillsTable, self.laborsTable]:
            t.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            t.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
            t.setShowGrid(False)
            horizheader = t.horizontalHeader()
            horizheader.setVisible(False)
            horizheader.setHighlightSections(False)
            horizheader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
            horizheader.setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            vertheader = t.verticalHeader()
            vertheader.setVisible(False)
            vertheader.setHighlightSections(False)
            vertheader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
            vertheader.setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)