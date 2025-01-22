from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QBrush, QColor, QPen, QPolygonF
from PyQt6.QtCore import Qt
import requests

class ClickableRectItem(QGraphicsRectItem):
    def __init__(self, rect, row, col):
        super().__init__(rect)
        self.row = row
        self.col = col
        self.enabled = False
        # Set the initial color based on enabled
        self.setBrush(QBrush(QColor(200, 255, 200))) if self.enabled else self.setBrush(QBrush(QColor(255, 200, 200)))
        self.setPen(QColor(0, 0, 0))

    def mousePressEvent(self, event):
        self.enabled = not self.enabled
        match self.enabled:
            case True:
                self.setBrush(QBrush(QColor(200, 255, 200)))  # green
            case False:
                self.setBrush(QBrush(QColor(255, 200, 200)))  # red

        super().mousePressEvent(event)


class ClickableGridView(QGraphicsView):
    def __init__(self, parent=None, rows=5, cols=5, cell_size=20, background_color=QBrush(QColor(200, 150, 100)), headers: list[str] = None, left_headers: list[str] = None):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.left_header_size = 50
        self.grid_start_x = 10 + self.left_header_size
        self.vborder_size = 10
        self.hborder_size = 0

        self.background_color = background_color

        self.draw_left_headers(left_headers)
        self.create_grid(self.rows, self.cols, self.cell_size, headers)

    def draw_column_header(self, col, header_text):
        header_text = QGraphicsTextItem(header_text)
        header_text.setDefaultTextColor(QColor(0, 0, 0))

        bounding = header_text.boundingRect()
        x_pos = self.grid_start_x + col * (self.cell_size + self.vborder_size)
        y_pos = -self.cell_size * 0.8 - 5

        header_text.setPos(x_pos, y_pos)
        header_text.setTransformOriginPoint(0, bounding.height())
        header_text.setRotation(-45)
        header_text.setZValue(1)

        box_item = QGraphicsRectItem(bounding)
        box_item.setPen(QPen(Qt.PenStyle.NoPen))
        box_item.setBrush(self.background_color)
        box_item.setPos(x_pos, y_pos)
        box_item.setTransformOriginPoint(0, bounding.height())
        box_item.setRotation(-45)
        box_item.setZValue(-1)
        self.scene.addItem(box_item)
        self.scene.addItem(header_text)

    def draw_left_headers(self, headers):
        for row in range(self.rows):
            header_text = QGraphicsTextItem(headers[row] if headers else f"Header {row}")
            header_text.setDefaultTextColor(QColor(0, 0, 0))

            # Position on the left
            x_pos = -self.cell_size * 0.5
            y_pos = (row * self.cell_size)
            header_text.setPos(x_pos, y_pos)
            header_text.setZValue(1)
            self.scene.addItem(header_text)

    def draw_background(self):
        """Draw a background rectangle behind the grid and headers."""
        total_width = self.cols * self.cell_size + 10
        total_height = self.rows * self.cell_size + self.cell_size  # grid rows + extra space for headers
        background_rect = QGraphicsRectItem(QRectF(0 - 10, -self.cell_size + 15, total_width + 10, total_height))
        background_rect.setBrush(self.background_color)
        background_rect.setZValue(-2)
        self.scene.addItem(background_rect)

        points = [
            QPointF(68.75 + self.left_header_size, -78.75),
            QPointF(total_width + 68.75, -78.75),
            QPointF(total_width, -5),
            QPointF(-10 + self.left_header_size, -5)
        ]

        polygon = QPolygonF(points)
        header_rect = self.scene.addPolygon(
            polygon,
            pen=QPen(Qt.PenStyle.NoPen),
            brush=self.background_color)  # Light-orange background
        header_rect.setZValue(-1)

    def create_grid(self, rows, cols, cell_size, headers):
        for col in range(cols):
            self.draw_column_header(col, headers[col])

            bg_left = (col * (cell_size + self.vborder_size) + self.left_header_size) - self.vborder_size / 2
            bg_width = cell_size + self.vborder_size
            if col == 0:
                bg_left -= self.vborder_size * 0.15
                bg_width += 15

            top_rect = QGraphicsRectItem(QRectF(
                bg_left,
                ((0 * cell_size) - self.hborder_size / 2) - 15,
                bg_width,
                cell_size + self.hborder_size
            ))

            top_rect.setPen(QPen(Qt.PenStyle.NoPen))
            top_rect.setBrush(self.background_color)
            top_rect.setZValue(-1)
            self.scene.addItem(top_rect)

            for row in range(rows):
                bg_rect = QGraphicsRectItem(QRectF(
                    bg_left,
                    (row * cell_size) - self.hborder_size / 2,
                    bg_width,
                    cell_size + self.hborder_size
                ))
                bg_rect.setPen(QPen(Qt.PenStyle.NoPen))
                bg_rect.setZValue(-1)
                bg_rect.setBrush(self.background_color)
                self.scene.addItem(bg_rect)

                clickable_rect = ClickableRectItem(QRectF(
                        col * (cell_size + self.vborder_size) + self.left_header_size,
                        row * cell_size,
                        cell_size,
                        cell_size
                    ),
                    row,
                    col
                )

                self.scene.addItem(clickable_rect)


if __name__ == '__main__':
    app = QApplication([])

    grid = ClickableGridView(rows=5, cols=5, cell_size=20, headers=["Header 1", "Header 2", "Header 3", "Header 4", "Header 5"])
    grid.show()
    app.exec()
