import pyautogui
import webbrowser
import asyncio
import win32api
import win32con
import logging
import psutil
import time
import json
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QMessageBox, QDialog, QHBoxLayout, QLineEdit, QFileDialog, QGraphicsOpacityEffect)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QPixmap, QPainter, QIcon

from .utility import resource_path, get_button_style
from .custom_warning_dialog import CustomWarningDialog
from .settings_dialog import SettingsDialog
from .generation_done_dialog import GenerationDoneDialog
from generator_card.WuWaCard import WuWaCard
from generator_card.src.tools.params import screen_name

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("assets/logo.png")))
        self.screen_width, self.screen_height = pyautogui.size()
        self.data_json = {}
        self.base_width = 2560
        self.base_height = 1440
        self.relative_positions = [
            (53, 202),
            (51, 383),
            (305, 1297),
            (2380, 56),
            (51, 560),
            (305, 1297),
            (661, 1317),
            (432, 246),
            (604, 246),
            (258, 455),
            (434, 455),
            (2380, 56),
            (51, 753),
            (51, 924)  
        ]

        
        self.path_selected = False
        self.positions = self.calculate_absolute_positions()
        self.supported_locales = ['en', 'ua', 'zh', 'hi', 'id']
        self.current_locale = self.load_current_locale()
        self.load_localization()
        self.game_process_name = "Wuthering Waves.exe"
        self.base_screenshot_dir = os.path.expanduser("screen")
        if not os.path.exists(self.base_screenshot_dir):
            os.makedirs(self.base_screenshot_dir)

        self.uid = "123456789"
        self.screenshot_dir = os.path.join(self.base_screenshot_dir, self.uid)

        self.initUI()

        self.check_game_timer = QTimer(self)
        self.check_game_timer.timeout.connect(self.check_game)
        self.check_game_timer.start(2000)

    def calculate_absolute_positions(self):
        positions = []
        scale_x = self.screen_width / self.base_width
        scale_y = self.screen_height / self.base_height
        
        for (x, y) in self.relative_positions:
            abs_x = int(x * scale_x)
            abs_y = int(y * scale_y)
            positions.append((abs_x, abs_y))
        
        return positions

    def load_current_locale(self):
        if os.path.exists(resource_path('current_locale.json')):
            with open(resource_path('current_locale.json'), 'r', encoding='utf-8') as file:
                return json.load(file)['locale']
        return 'en'

    def save_current_locale(self, locale_code):
        with open(resource_path('current_locale.json'), 'w', encoding='utf-8') as file:
            json.dump({'locale': locale_code}, file)

    def load_localization(self):
        if self.current_locale not in self.supported_locales:
            self.current_locale = 'en'
        self.localization = self.load_json(self.current_locale)

    def load_json(self, lang_code):
        file_path = f'locales/{lang_code}.json'
        if os.path.exists(resource_path(file_path)):
            with open(resource_path(file_path), 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            with open(resource_path('locales/en.json'), 'r', encoding='utf-8') as file:
                return json.load(file)

    def initUI(self):
        self.setWindowTitle(self.localization['localization']['app_title'])
        self.background_pixmap = QPixmap(resource_path("assets/bg.png"))
        layout = QVBoxLayout()

        self.title_label = QLabel(self.localization['localization']['title'])
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.status_label = QLabel(self.localization['localization']['status_not_detected'])
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(self.status_label)

        self.navigation_label = QLabel(self.localization['localization']['navigation'])
        self.navigation_label.setAlignment(Qt.AlignCenter)
        self.navigation_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.navigation_label)

        self.uid_label = QLabel("UID:")
        self.uid_label.setAlignment(Qt.AlignCenter)
        self.uid_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.uid_label)

        self.uid_input = QLineEdit(self.uid)
        self.uid_input.setAlignment(Qt.AlignCenter)
        self.uid_input.setStyleSheet("font-size: 14px; padding: 5px;")
        self.uid_input.textChanged.connect(self.update_uid)
        layout.addWidget(self.uid_input)

        self.start_button = QPushButton(self.localization['localization']['launch'])
        self.start_button.setStyleSheet(get_button_style())
        self.start_button.clicked.connect(self.start_screenshot_task)
        layout.addWidget(self.start_button)

        self.folder_button = QPushButton(self.localization['localization']['folder'])
        self.folder_button.setStyleSheet(get_button_style())
        self.folder_button.clicked.connect(self.choose_folder)
        layout.addWidget(self.folder_button)

        self.generation_button = QPushButton(self.localization['localization']['generation'])
        self.generation_button.setStyleSheet(get_button_style())
        self.generation_button.clicked.connect(self.run_generation_task)
        layout.addWidget(self.generation_button)

        self.exit_button = QPushButton(self.localization['localization']['exit'])
        self.exit_button.setStyleSheet(get_button_style())
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        folder_path_layout = QHBoxLayout()
        folder_path_layout.addStretch()
        self.screenshot_path = QLabel(self.screenshot_dir)
        self.screenshot_path.setStyleSheet("color: white; font-size: 10px; margin-top: 10px;")
        folder_path_layout.addWidget(self.screenshot_path)
        folder_path_layout.addStretch()

        layout.addLayout(folder_path_layout)

        self.icon_layout = QHBoxLayout()

        self.settings_button = self.create_button('assets/icon/settings.png', self.open_settings)
        self.github_button = self.create_button('assets/icon/github.png', self.open_github)
        self.discord_button = self.create_button('assets/icon/discord.png', self.open_discord)
        self.info_button = self.create_button('assets/icon/information.png', self.show_info)

        layout.addLayout(self.icon_layout)
        self.setLayout(layout)
        self.show()

    def create_button(self, icon_path, callback):
            button = QPushButton()
            button.setIcon(QIcon(resource_path(icon_path)))
            button.setIconSize(QSize(24, 24))
            button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
            button.clicked.connect(callback)
            self.icon_layout.addWidget(button)
            
            return button
        
    def open_github(self):
        webbrowser.open('https://github.com/DEViantUA/WuWaScreenCard')

    def open_discord(self):
        webbrowser.open('https://discord.gg/rKrbqz5utj')
    
    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, self.localization['localization']['select_folder'], self.base_screenshot_dir)
        if folder:
            self.base_screenshot_dir = folder
            self.screenshot_dir = os.path.join(self.base_screenshot_dir, self.uid)
            self.screenshot_path.setText(self.screenshot_dir)
            self.path_selected = True

    def update_uid(self):
        self.uid = self.uid_input.text()
        self.screenshot_dir = os.path.join(self.base_screenshot_dir, self.uid)
        self.screenshot_path.setText(self.screenshot_dir)

    def paintEvent(self, event):
        painter = QPainter(self)
        scaled_pixmap = self.background_pixmap.scaled(self.size(), aspectRatioMode=Qt.KeepAspectRatioByExpanding)
        painter.drawPixmap(0, 0, scaled_pixmap)

    def check_game(self):
        if self.is_game_running():
            self.status_label.setText(self.localization['localization']['status_detected'])
            self.status_label.setStyleSheet("color: green; font-size: 14px; margin-bottom: 20px;")
        else:
            self.status_label.setText(self.localization['localization']['status_not_detected'])
            self.status_label.setStyleSheet("color: red; font-size: 14px; margin-bottom: 20px;")
    
    def is_game_running(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == self.game_process_name:
                return True
        return False

    def start_screenshot_task(self):
        if not self.path_selected:
            dlg = CustomWarningDialog(self.localization)
            dlg.exec_()
            return
        
        if self.is_game_running():
            self.create_folder()
            self.run_screenshot_task()

    def create_folder(self):
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def run_screenshot_task(self):
        for index, position in enumerate(self.positions):
            self.click_and_screenshot(position, index)
        
        self.click(self.positions[0])
        time.sleep(2)

        QMessageBox.information(self, self.localization['localization']['information'], self.localization['localization']['script_completed'])
    
    def click_and_screenshot(self, position, index):
        self.click(position)
        if index in [0,5,12]:
            time.sleep(3)
        elif index == 5:
            return
        else:
            time.sleep(1)

        screenshot_path = os.path.join(self.screenshot_dir, f"{screen_name.get(index)}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        time.sleep(1)

    def click(self, position):
        x, y = position
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def open_settings(self):
        settings_dialog = SettingsDialog(self, self.current_locale)
        if settings_dialog.exec_() == QDialog.Accepted:
            selected_locale = settings_dialog.language_combo.currentData()
            self.localization = self.load_json(selected_locale)
            self.update_ui_text()
            self.current_locale = selected_locale
            self.save_current_locale(selected_locale)

    def update_ui_text(self):
        self.setWindowTitle(self.localization['localization']['app_title'])
        self.title_label.setText(self.localization['localization']['title'])
        self.status_label.setText(self.localization['localization']['status_not_detected'])
        self.navigation_label.setText(self.localization['localization']['navigation'])
        self.start_button.setText(self.localization['localization']['launch'])
        self.folder_button.setText(self.localization['localization']['folder'])
        self.generation_button.setText(self.localization['localization']['generation'])
        self.exit_button.setText(self.localization['localization']['exit'])
        

    def show_info(self):
        info_dialog = QDialog(self)
        info_dialog.setWindowTitle(self.localization['localization']['information'])
        info_dialog.setFixedSize(850, 800)

        info_dialog.setStyleSheet("background-color: #1e1e1e;")

        image_label = QLabel(info_dialog)
        image_pixmap = QPixmap(resource_path('assets/bg.png'))
        image_label.setPixmap(image_pixmap)
        image_label.setGeometry(info_dialog.rect())
        image_label.setScaledContents(True)

        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.2)
        image_label.setGraphicsEffect(opacity_effect)
        image_label.raise_()

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("WuWaScreenCard")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background: transparent;")
        layout.addWidget(title_label)

        instructions_label = QLabel(self.localization['localization']['desc_info_one'])
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("font-size: 16px; color: white; margin: 10px 0; background: transparent;")
        layout.addWidget(instructions_label)

        screenshot_label = QLabel()
        pixmap = QPixmap(resource_path('assets/tutorial.png'))
        scaled_pixmap = pixmap.scaled(532, 298, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        screenshot_label.setPixmap(scaled_pixmap)
        screenshot_label.setAlignment(Qt.AlignCenter)
        screenshot_label.setStyleSheet("background: transparent;")
        layout.addWidget(screenshot_label)

        layout.addSpacing(10)

        instructions_label_2 = QLabel(self.localization['localization']['desc_info_two'])
        instructions_label_2.setAlignment(Qt.AlignCenter)
        instructions_label_2.setStyleSheet("font-size: 16px; color: white; margin: 10px 0; background: transparent;")
        layout.addWidget(instructions_label_2)

        close_button = QPushButton(self.localization['localization']['close'])
        close_button.setStyleSheet(get_button_style())
        close_button.clicked.connect(info_dialog.accept)
        
        video_button = QPushButton()
        video_button.setIcon(QIcon(resource_path('assets/icon/video.png')))
        video_button.setIconSize(QSize(20, 20))
        video_button.setStyleSheet(get_button_style())
        video_button.clicked.connect(self.open_video_tutorial)

        button_layout = QHBoxLayout()
        button_layout.addWidget(video_button)
        button_layout.addWidget(close_button)
        
        button_layout.setAlignment(Qt.AlignCenter)

        layout.addLayout(button_layout)
        
        info_dialog.setLayout(layout)
        info_dialog.exec_()

    def open_video_tutorial(self):
        webbrowser.open('https://drive.google.com/file/d/1WtF-5yvF-WEl0QcnmQHhA-wMZ2741EDo/view?usp=sharing')

    
    async def start_generation(self):
        async with WuWaCard(self.uid, os.path.join(self.screenshot_dir), pyautogui.size()) as card:
            return await card.start()

    def delete_non_card_files(self):
        files = os.listdir(self.screenshot_dir)
        for file_name in files:
            file_path = os.path.join(self.screenshot_dir, file_name)
            if os.path.isfile(file_path) and 'card_' not in file_name:
                os.remove(file_path)

    def run_generation_task(self):
        
        if not self.path_selected:
            dlg = CustomWarningDialog(self.localization)
            dlg.exec_()
            return
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            card = loop.run_until_complete(self.start_generation())
        except Exception as e:
            logging.exception(self.base_screenshot_dir)
            logging.exception("Error during generation task")
            loop.close()
            raise
            return
        
        name = int(time.time())
        card_path = f"{self.screenshot_dir}/card_{name}.png"
        card.save(card_path)
        self.delete_non_card_files()

        dlg = GenerationDoneDialog(card_path, self.screenshot_dir, self.localization)
        dlg.exec_()

        loop.close()