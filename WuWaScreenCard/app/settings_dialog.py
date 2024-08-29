from PyQt5.QtWidgets import (QVBoxLayout, QPushButton, QLabel, 
                             QComboBox, QDialog, QHBoxLayout)
from PyQt5.QtGui import  QIcon
from .utility import resource_path

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_locale=None):
        super(SettingsDialog, self).__init__(parent)
        self.localization = parent.localization
        self.setWindowTitle(self.localization['localization']['settings'])
        self.setFixedWidth(300)

        layout = QVBoxLayout()
        label = QLabel(self.localization['localization']['choose_language'])
        layout.addWidget(label)

        self.language_combo = QComboBox(self)
        self.language_combo.addItem(QIcon(resource_path("assets/localization/en.png")), "English", "en")
        self.language_combo.addItem(QIcon(resource_path("assets/localization/ua.png")), "Українська", "ua")
        self.language_combo.addItem(QIcon(resource_path("assets/localization/zh.png")), "中文", "zh")
        self.language_combo.addItem(QIcon(resource_path("assets/localization/hi.png")), "हिन्दी", "hi")
        self.language_combo.addItem(QIcon(resource_path("assets/localization/id.png")), "Bahasa Indonesia", "id")
        layout.addWidget(self.language_combo)
        
        index = self.language_combo.findData(current_locale)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        button_box = QHBoxLayout()
        save_button = QPushButton(self.localization['localization']['save'])
        save_button.clicked.connect(self.accept)
        button_box.addWidget(save_button)
        
        layout.addLayout(button_box)
        self.setLayout(layout)
