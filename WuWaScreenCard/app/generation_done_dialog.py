
import os
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel,QDialog,QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from .utility import resource_path, get_button_style

class GenerationDoneDialog(QDialog):
    def __init__(self, card_path, folder_path, localization, parent=None):
        super().__init__(parent)
        self.card_path = card_path
        self.folder_path = folder_path
        self.localization = localization

        self.setWindowIcon(QIcon(resource_path("assets/logo.png")))
        self.setWindowTitle(self.localization['localization']['app_title'])
        self.setFixedSize(900, 472)

        self.background_label = QLabel(self)
        background_pixmap = QPixmap(resource_path("assets/generation.png")).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.background_label.setPixmap(background_pixmap)
        self.background_label.setGeometry(0, 0, 900, 472)


        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 10)

        title_label = QLabel(self)
        title_label.setText("Image generation is ready!")
        title_label.setStyleSheet("color: white; font-size: 24px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(50)
        main_layout.addWidget(title_label)

        card_label = QLabel(self)
        card_pixmap = QPixmap(self.card_path).scaled(575, 234, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        card_label.setPixmap(card_pixmap)
        card_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(card_label)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)

        open_folder_button = QPushButton(self.localization["localization"]["open_folder"])
        open_folder_button.setStyleSheet(get_button_style())
        open_folder_button.clicked.connect(self.open_folder)
        button_layout.addWidget(open_folder_button)

        close_button = QPushButton(self.localization["localization"]["close"])
        close_button.setStyleSheet(get_button_style())
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        button_widget = QWidget(self)
        button_widget.setLayout(button_layout)
        main_layout.addWidget(button_widget)

        self.setLayout(main_layout)

    def open_folder(self):
        os.startfile(self.folder_path)

    def exec_(self):
        self.background_label.lower()
        super().exec_()
