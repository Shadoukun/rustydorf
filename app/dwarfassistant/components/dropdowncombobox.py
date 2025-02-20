from PyQt6.QtWidgets import QApplication, QComboBox, QMenu, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QAction

class SortComboBox(QWidget):
    """This widget is a combination of a QComboBox and a QPusbutton for sorting
        The sort button is positioned near the right edge of the combo box.

        It accepts an optional custom QComboBox to use
    """
    def __init__(self, parent=None, custom_combobox=None):

        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
        self.create_combobox(custom_combobox)

        self.sort_button = QPushButton("↑↓", self)
        self.sort_button.setFixedSize(24, 24)

    def create_combobox(self, widget=None):
        """
        Create the combo box and add it to the layout
        """

        if widget is None:
            widget = DropdownComboBox(self)

        self.combo = widget
        self.main_layout.addWidget(self.combo)

    def resizeEvent(self, event):
        """
        Position the sort button near the right edge of the combo box
        and move it each time the widget is resized.
        """

        super().resizeEvent(event)
        if self.combo is None:
            return

        geom = self.combo.geometry()
        btn_width = self.sort_button.width()
        btn_height = self.sort_button.height()

        # position the sort button
        x = geom.right() - btn_width - 25
        y = geom.top() + (geom.height() - btn_height) // 2

        self.sort_button.move(x, y)

class DropdownComboBox(QComboBox):
    """Custom QComboBox that displays a custom QMenu when the popup is shown"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.menu_data = {}

    def showPopup(self):
        # instead of the default popup show a custom QMenu
        menu = QMenu(self)
        menu.setFixedWidth(self.width())
        self.populate_menu(menu, self.menu_data)
        pos = self.mapToGlobal(QPoint(0, self.height()))
        action = menu.exec(pos)


    def populate_menu(self, menu, data):
        """
        Recursively populate the QMenu based on the structure of data.
        data can be a dict for submenus or a list of strings for leaf items.

        Example:
            data = {
                "Fruits": ["Apple", "Banana", "Cherry"],
                "Vegetables": {
                    "Leafy": ["Lettuce", "Spinach"],
                    "Root": ["Carrot", "Potato"]
                },
                "Meats": ["Chicken", "Beef", "Pork"]
            }
        """

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    submenu = QMenu(key, menu)
                    self.populate_menu(submenu, value)
                    menu.addMenu(submenu)
                else:
                    # its not a dict or list just create a single action
                    action = QAction(str(value), menu)
                    action.setData(value)
                    menu.addAction(action)
        elif isinstance(data, list):
            for item in data:
                action = QAction(str(item), menu)
                action.setData(item)
                menu.addAction(action)
        else:
            # its not a dict or list just create a single action
            action = QAction(str(data), menu)
            action.setData(data)
            menu.addAction(action)

    # TODO: add a method to add new items to the menu_data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dropdown Test")
        layout = QVBoxLayout()
        self.dropdown_combo = SortComboBox(self)
        self.dropdown_combo.combo.menu_data = {
            "Fruits": ["Apple", "Banana", "Cherry"],
            "Vegetables": {
                "Leafy": ["Lettuce", "Spinach"],
                "Root": ["Carrot", "Potato"]
            },
            "Meats": ["Chicken", "Beef", "Pork"]
        }
        layout.addWidget(self.dropdown_combo)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
