from PyQt6.QtWidgets import (QDialog, QWidget, QHBoxLayout, QSpinBox,
    QVBoxLayout, QLabel, QCheckBox, QPushButton, QFontDialog, QTabWidget
)
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from .signals import SignalsManager

DEFAULT_FONT_NAME = "More Perfect DOS VGA"
DEFAULT_FONT_SIZE = 6

class SettingsMenuDialog(QDialog):
    def __init__(self, settings: QSettings):
        super().__init__()
        self.setWindowTitle("Settings")
        self.settings = settings
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        general_tab = QWidget()
        general_tab_layout = QVBoxLayout()
        general_tab.setLayout(general_tab_layout)
        self.font_selector = FontSelectorWidget(self, settings)
        self.font_selector.setObjectName("fontSelector")
        general_tab_layout.addWidget(self.font_selector)
        self.tab_widget.addTab(general_tab, "General")

        namelist_tab = QWidget()
        namelist_tab_layout = QVBoxLayout()
        namelist_tab.setLayout(namelist_tab_layout)
        self.tab_widget.addTab(namelist_tab, "Name List")

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_wrapper = QWidget()
        button_wrapper.setLayout(button_layout)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        layout.addWidget(button_wrapper)

    def save_settings(self):
        print("Saving Settings")
        print(f"Font: {self.font_selector.current_font.family()}, Size: {self.font_selector.current_font.pointSize()}")
        self.settings.setValue("font_name", self.font_selector.current_font.family())
        self.settings.setValue("font_size", self.font_selector.current_font.pointSize())
        SignalsManager.instance().refresh_ui.emit()
        self.accept()

class FontSelectorWidget(QWidget):
    def __init__(self, parent=None, settings: QSettings = None):
        super().__init__(parent)
        font_name = settings.value("font_name", DEFAULT_FONT_NAME, type=str)
        font_size = settings.value("font_size", DEFAULT_FONT_SIZE, type=int)

        self.current_font = QFont(font_name, font_size)
        self.font_label = QLabel(f"Font: {self.current_font.family()}, {self.current_font.pointSize()}")
        self.edit_button = QPushButton("Change Font")

        layout = QHBoxLayout()
        layout.addWidget(self.font_label)
        layout.addWidget(self.edit_button)
        self.setLayout(layout)

        self.edit_button.clicked.connect(self.edit_font)

    def edit_font(self):
        font, ok = QFontDialog.getFont(self.current_font, self, "Select Font")
        if ok:
            self.current_font = font
            self.font_label.setText(f"Font:  {self.current_font.family()}, {self.current_font.pointSize()}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    settings = QSettings("dwarfassistant", "dwarfassistant")
    window = SettingsMenuDialog(settings)
    window.show()
    sys.exit(app.exec())