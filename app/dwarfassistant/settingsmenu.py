from PyQt6.QtWidgets import (QDialog, QWidget, QHBoxLayout, QSpinBox,
    QVBoxLayout, QLabel, QCheckBox, QPushButton
)

class SettingsMenuDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")

        layout = QVBoxLayout()
        layout2 = QHBoxLayout()
        layout.addLayout(layout2)

        column1 = QWidget()
        column1_layout = QVBoxLayout()
        column1.setLayout(column1_layout)
        layout2.addWidget(column1)

        # Font Size
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        font_size_layout.addWidget(font_size_label)
        self.font_size_num = QSpinBox()
        self.font_size_num.setRange(4, 24)
        self.font_size_num.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        font_size_layout.addWidget(self.font_size_num)
        column1_layout.addLayout(font_size_layout)

        column2 = QWidget()
        column2_layout = QVBoxLayout()
        column2.setLayout(column2_layout)
        layout2.addWidget(column2)

        self.enable_rightpanel_tabs = QCheckBox("Enable Right Panel Tabs")
        column2_layout.addWidget(self.enable_rightpanel_tabs)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_wrapper = QWidget()
        button_wrapper.setLayout(button_layout)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        layout.addWidget(button_wrapper)
        self.setLayout(layout)

    def save_settings(self):
        print("Font Size:", self.font_size_num.value())
        print("Right Tabs Enabled:", self.enable_rightpanel_tabs.isChecked())
        self.accept()
