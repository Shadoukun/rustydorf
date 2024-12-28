# Form implementation generated from reading ui file '.\app\dwarfassistant\dwarfinfotab.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget
from .infoattributeswidget import InfoAttributesWidget


class DwarfInfoTabUI(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())

        Form.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setKerning(True)
        Form.setFont(font)

        # self.traitsTable = QtWidgets.QTableWidget(parent=Form)
        # self.traitsTable.setGeometry(QtCore.QRect(235, 5, 111, 271))
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.traitsTable.sizePolicy().hasHeightForWidth())
        # self.traitsTable.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setFamily("More Perfect DOS VGA")
        # self.traitsTable.setFont(font)
        # self.traitsTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.traitsTable.setObjectName("traitsTable")
        # self.traitsTable.setColumnCount(2)
        # self.traitsTable.setRowCount(1)
        # item = QtWidgets.QTableWidgetItem()
        # self.traitsTable.setVerticalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.traitsTable.setHorizontalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.traitsTable.setHorizontalHeaderItem(1, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.traitsTable.setItem(0, 0, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.traitsTable.setItem(0, 1, item)
        # self.traitsTable.horizontalHeader().setDefaultSectionSize(86)
        # self.traitsTable.verticalHeader().setVisible(False)

        # self.thoughtsTable = QtWidgets.QTableWidget(parent=Form)
        # self.thoughtsTable.setGeometry(QtCore.QRect(10, 280, 451, 195))
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.thoughtsTable.sizePolicy().hasHeightForWidth())
        # self.thoughtsTable.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setFamily("More Perfect DOS VGA")
        # self.thoughtsTable.setFont(font)
        # self.thoughtsTable.setObjectName("thoughtsTable")
        # self.thoughtsTable.setColumnCount(1)
        # self.thoughtsTable.setRowCount(0)
        # item = QtWidgets.QTableWidgetItem()
        # self.thoughtsTable.setHorizontalHeaderItem(0, item)
        # self.thoughtsTable.horizontalHeader().setStretchLastSection(True)

        # self.infoLabel = QtWidgets.QLabel(parent=Form)
        # self.infoLabel.setGeometry(QtCore.QRect(10, 10, 191, 61))
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.infoLabel.sizePolicy().hasHeightForWidth())
        # self.infoLabel.setSizePolicy(sizePolicy)
        # font = QtGui.QFont()
        # font.setFamily("More Perfect DOS VGA")
        # font.setPointSize(7)
        # self.infoLabel.setFont(font)
        # self.infoLabel.setObjectName("infoLabel")
        # self.line = QtWidgets.QFrame(parent=Form)
        # self.line.setGeometry(QtCore.QRect(461, 10, 10, 441))
        # self.line.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        # self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.line.setObjectName("line")

        # self.skillStack = QtWidgets.QStackedWidget(parent=Form)
        # self.skillStack.setGeometry(QtCore.QRect(469, 35, 151, 445))
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.skillStack.sizePolicy().hasHeightForWidth())
        # self.skillStack.setSizePolicy(sizePolicy)
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