
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSettings

class RightPanelWidget(QtWidgets.QWidget):
    """
    This is the the right panel widget that contains the Skills and Labors tables.
    """

    def __init__(self, parent, settings: QSettings):
        super().__init__(parent)
        self.setObjectName("rightPanel")
        self.setMinimumWidth(151)
        self.setMaximumWidth(200)

        font_name = settings.value("font_name", "More Perfect DOS VGA", type=str)
        font_size = settings.value("font_size", 6, type=int)
        font = QtGui.QFont(font_name, font_size)
        self.setFont(font)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

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
        self.gridlayout.addWidget(self.buttonWidget, 0, 0, 1, 3)

        ## Skills Button

        self.skillsButton = QtWidgets.QPushButton(self) # Attributes Button
        btnSizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.skillsButton.setSizePolicy(btnSizePolicy)
        self.skillsButton.setFont(font)
        self.skillsButton.setText("Skills")
        buttonlayout.addWidget(self.skillsButton)

        ## Traits Button

        self.traitsButton = QtWidgets.QPushButton(self) # Traits Button
        self.traitsButton.setSizePolicy(btnSizePolicy)
        self.traitsButton.setFont(font)
        self.traitsButton.setText("Traits")
        buttonlayout.addWidget(self.traitsButton)


        # Stack Widget

        self.stackWidget = QtWidgets.QStackedWidget(parent=self)
        self.stackWidget.setObjectName("stackWidget")
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

        # Traits Page

        self.traitsPage = QtWidgets.QWidget()
        self.traitsPage.setObjectName("traitsPage")
        layout = QtWidgets.QVBoxLayout(self.traitsPage)
        layout.setContentsMargins(0, 0, 0, 0)
        self.traitsPage.setLayout(layout)
        self.stackWidget.addWidget(self.traitsPage)

        ### Traits Table

        self.traitsTable = QtWidgets.QTableWidget(parent=self.traitsPage)
        self.traitsTable.setObjectName("traitsTable")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.traitsTable.sizePolicy().hasHeightForWidth())
        self.traitsTable.setSizePolicy(sizePolicy)
        self.traitsTable.setFont(font)
        self.traitsTable.setColumnCount(0)
        self.traitsTable.setRowCount(0)
        layout.addWidget(self.traitsTable)

        # Common Table Settings

        for t in [self.skillsTable, self.traitsTable]:
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