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
        self.cell_size = 20
        self.left_header_size = 125
        self.background_color = background_color

        self.draw_background()
        self.draw_top_headers(headers)
        self.draw_left_headers(left_headers)
        self.create_grid(self.rows, self.cols, self.cell_size)

    def draw_top_headers(self, headers):
        for col in range(self.cols):
            header_text = QGraphicsTextItem(headers[col] if headers else f"Header {col}")
            header_text.setDefaultTextColor(QColor(0, 0, 0))

            # Calculate boundingRect for the text
            bounding = header_text.boundingRect()
            x_pos = col * self.cell_size + 10 + self.left_header_size
            y_pos = -self.cell_size * 0.8 - 5

            # move and pivot the text
            header_text.setPos(x_pos, y_pos)
            header_text.setTransformOriginPoint(0, bounding.height())
            header_text.setRotation(-45)
            header_text.setZValue(1)
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

        # Define the four corners of the trapezoid for the background behind the headers
        # top-left counter-clockwise
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

    def create_grid(self, rows, cols, cell_size):
        """Create a grid layout with rows x cols cells of size cell_size x cell_size."""
        for row in range(rows):
            for col in range(cols):
                rect = QRectF(col * cell_size + self.left_header_size, row * cell_size, cell_size, cell_size)
                rect_item = ClickableRectItem(rect, row, col)
                self.scene.addItem(rect_item)

if __name__ == '__main__':
    app = QApplication([])

    response: list[dict] = requests.get('http://127.0.0.1:3000/data').json()
    grid = ClickableGridView(rows=5, cols=len(response["labors"]), cell_size=20, headers=[labor['name'] for labor in response['labors']])
    grid.show()
    app.exec()
