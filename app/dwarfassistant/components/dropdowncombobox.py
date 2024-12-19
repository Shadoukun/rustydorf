from PyQt6.QtWidgets import (
    QApplication, QComboBox, QMenu, QMessageBox, QMainWindow, QWidget, QVBoxLayout
)
from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QAction

class DropdownComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        # empty data for populate_menu
        self.menu_data = {}

    def showPopup(self):
        # instead of the default popup show a custom QMenu
        menu = QMenu(self)

        self.populate_menu(menu, self.menu_data)

        # position the menu below the combo box
        pos = self.mapToGlobal(QPoint(0, self.height()))
        action = menu.exec(pos)

        # if an action was triggered update the QComboBox text
        if action and action.data() is not None:
            # TODO: transform keywords, @attr, etc based on menu_data selection
            #       Or remove keywords. I'm not sure I need them. if I use this
            self.setCurrentText(action.text())

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
        self.dropdown_combo = DropdownComboBox()
        self.dropdown_combo.menu_data = {
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
