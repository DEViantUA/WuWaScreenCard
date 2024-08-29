from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel,QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from .utility import resource_path, get_button_style


class CustomWarningDialog(QDialog):
    def __init__(self, localization, parent=None):
        super().__init__(parent)
        self.localization = localization
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon(resource_path("assets/logo.png")))
        self.setWindowTitle(self.localization['localization']['app_title'])
        self.setFixedSize(412, 198)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        self.background_label = QLabel(self)
        pixmap = QPixmap(resource_path("assets/warn.png"))
        self.background_label.setPixmap(pixmap)
        self.background_label.setFixedSize(450, 198)
        self.background_label.setScaledContents(True)

        self.icon_label = QLabel(self)
        icon_pixmap = QPixmap(resource_path("assets/icon/warn.png"))
        self.icon_label.setPixmap(icon_pixmap)
        self.icon_label.setAlignment(Qt.AlignCenter)
        
        self.warning_label = QLabel(self.localization['localization']['warning'], self)
        self.warning_label.setStyleSheet("color: yellow; font-size: 24px;")
        self.warning_label.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel(self.localization['localization']['please_select_folder'], self)
        self.info_label.setStyleSheet("color: white; font-size: 16px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)

        self.ok_button = QPushButton(self.localization["localization"]["close"], self)
        self.ok_button.setStyleSheet(get_button_style())
        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.warning_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.info_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def exec_(self):
        self.background_label.lower()
        super().exec_()