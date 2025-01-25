import sys
from math import sqrt, sin, acos, hypot, degrees, radians, ceil
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QRectF

# Custom header view with angled labels
class AngledHeader(QtWidgets.QHeaderView):
    borderPen = QtGui.QColor("black")
    labelBrush = QtGui.QColor("#5C4033")

    def __init__(self, parent=None, **kwargs):
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
        self.border_size = 2
        self.header_height = 100
        self.labelBrush = kwargs.get('labelBrush', self.labelBrush)

        # Set default section s
        # ize based on font metrics
        fm = self.fontMetrics()
        self.setDefaultSectionSize(int(sqrt((fm.height() + 4) ** 2 * 2)))
        self.setSectionsClickable(True)
        self.setMaximumHeight(self.header_height)
        self.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)

        # Calculate size for text ellipsis
        self.fontEllipsisSize = int(hypot(*[fm.height()] * 2) * 0.5)

    def sizeHint(self):
        hint = super().sizeHint()
        count = self.count()
        if not count:
            return hint

        fm = self.fontMetrics()
        width = self.defaultSectionSize()
        hint.setWidth(width * count + self.minimumHeight())

        maxDiag = maxWidth = maxHeight = 1
        for s in range(count):
            if self.isSectionHidden(s):
                continue
            rect = fm.boundingRect(str(self.model().headerData(s, QtCore.Qt.Orientation.Horizontal)) + '    ')
            diag = max(1, hypot(rect.width(), rect.height()))
            if diag > maxDiag:
                maxDiag = diag
                maxWidth = max(1, rect.width())
                maxHeight = max(1, rect.height())

        # Calculate angle using law of cosines
        angle = degrees(acos(
            (maxDiag ** 2 + maxWidth ** 2 - maxHeight ** 2) / (2.0 * maxDiag * maxWidth)
        ))
        minSize = max(width, sin(radians(angle + 45)) * maxDiag)
        hint.setHeight(min(self.maximumHeight(), minSize))
        return hint

    # def mousePressEvent(self, event):
    #         width = self.defaultSectionSize()
    #         start = self.sectionViewportPosition(0)
    #         rect = QtCore.QRect(0, 0, width, -self.height())
    #         transform = QtGui.QTransform().translate(0, self.height()).shear(-1, 0)

    #         for s in range(self.count()):
    #             if self.isSectionHidden(s):
    #                 continue
    #             # Note: In PyQt6, WindingFill is QtCore.Qt.FillRule.WindingFill
    #             polygon = transform.mapToPolygon(rect.translated(s * width + start, 0))
    #             if polygon.containsPoint(event.position().toPoint(), QtCore.Qt.FillRule.WindingFill):
    #                 # Use sectionPressed(s) if available; otherwise consider sectionClicked(s).
    #                 self.sectionPressed.emit(s)
    #                 return

    def paintEvent(self, event):
        qp = QtGui.QPainter(self.viewport())
        qp.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing, True)
        width = self.defaultSectionSize()
        delta = self.height()

        qp.translate(self.sectionViewportPosition(0) - 0.5, -0.5)
        fmDelta = (self.fontMetrics().height() - self.fontMetrics().descent()) * 0.5
        rect = QtCore.QRectF(0, 0, width, -delta)
        diagonal = hypot(delta, delta)

        for s in range(self.count()):
            if self.isSectionHidden(s):
                continue

            qp.save()
            qp.save()
            qp.setPen(self.borderPen)
            qp.setTransform(qp.transform().translate(s * width, delta).shear(-1, 0))
            qp.drawRect(rect)
            qp.setPen(QtCore.Qt.PenStyle.NoPen)
            qp.setBrush(self.labelBrush)

            # Draw header border
            qp.drawRect(rect.adjusted(self.border_size, -self.border_size, -self.border_size, self.border_size))
            qp.restore()

            qp.translate(s * width + width, delta)
            qp.rotate(-45)

            label = str(self.model().headerData(s, QtCore.Qt.Orientation.Horizontal))
            # Elide text if it's too long
            elidedLabel = self.fontMetrics().elidedText(
                label, QtCore.Qt.TextElideMode.ElideRight, int(diagonal - self.fontEllipsisSize)
            )
            qp.drawText(0, int(-fmDelta) -2, elidedLabel)
            qp.restore()


# Custom table view with angled headers and checkable items
class CheckableAngledTable(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHorizontalHeader(AngledHeader(self))
        self.verticalScrollBarSpacer = QtWidgets.QWidget()
        self.addScrollBarWidget(self.verticalScrollBarSpacer, QtCore.Qt.AlignmentFlag.AlignTop)
        self.fixLock = False

    def mousePressEvent(self, event):
        index = self.indexAt(event.position().toPoint())
        item = self.model().itemFromIndex(index)
        print(item)
        if item:
            enabled = item.checkState() == QtCore.Qt.CheckState.Checked
            print(f'Cell {index.row()},{index.column()} is enabled: {enabled}')
            if enabled:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Checked)

    def setModel(self, model):
        if self.model():
            self.model().headerDataChanged.disconnect(self.fixViewport)
        super().setModel(model)
        model.headerDataChanged.connect(self.fixViewport)

    def fixViewport(self):
        if self.fixLock:
            return
        self.fixLock = True
        QtCore.QTimer.singleShot(0, self.delayedFixViewport)

    def delayedFixViewport(self):
        QtWidgets.QApplication.processEvents()
        header = self.horizontalHeader()
        if not header.isVisible():
            self.verticalScrollBarSpacer.setFixedHeight(0)
            self.updateGeometries()
            self.fixLock = False
            return

        self.verticalScrollBarSpacer.setFixedHeight(header.sizeHint().height())
        bar = self.horizontalScrollBar()
        bar.blockSignals(True)
        step = bar.singleStep() * (header.height() / header.defaultSectionSize())
        bar.setMaximum(bar.maximum() + int(step))
        bar.blockSignals(False)
        self.fixLock = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fixViewport()


# Delegate for rendering custom checkable table items
class CheckedTableItemDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.flags() & QtCore.Qt.ItemFlag.ItemIsUserCheckable:
            item = index.model().itemFromIndex(index)

            border_size = self.parent().horizontalHeader().border_size
            rect = option.rect.adjusted(5 + border_size, 5, -5 + border_size, -5)
            size = min(rect.width(), rect.height())
            rect = QRectF(
                rect.x() + (rect.width() - size) / 2,
                rect.y() + (rect.height() - size) / 2,
                size,
                size
            )
            checked = item.checkState()
            painter.setBrush(QtGui.QColor("red") if checked == QtCore.Qt.CheckState.Unchecked else QtGui.QColor("green"))

            if checked == QtCore.Qt.CheckState.Checked:
                painter.fillRect(rect, QtGui.QColor("green"))
            else:
                painter.fillRect(rect, QtGui.QColor("red"))


class TestWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self.table = CheckableAngledTable()
        layout.addWidget(self.table)

        model = QtGui.QStandardItemModel(4, 5)
        for r in range(4):
            for c in range(5):
                item = QtGui.QStandardItem(f'{r},{c}')
                item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                model.setItem(r, c, item)

        self.table.setModel(model)
        self.table.setItemDelegate(CheckedTableItemDelegate(self.table))
        self.table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Set header labels
        model.setVerticalHeaderLabels([f'Location {i + 1}' for i in range(8)])
        columns = [f'Column {c + 1}' for c in range(8)]
        columns[3] += ' very, very, very, very, very, very, long'
        model.setHorizontalHeaderLabels(columns)

        self.table.verticalHeader().setDefaultSectionSize(10)  # Set vertical header size

        # Apply styles to headers and grid lines
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: gray;
                color: black;
                font-weight: bold;
                border: 1px solid #444;
            }
            QTableView {
                gridline-color: transparent;
            }
        """)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = TestWidget()
    w.show()
    sys.exit(app.exec())
