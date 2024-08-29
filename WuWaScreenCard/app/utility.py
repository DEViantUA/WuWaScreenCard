import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_button_style():
        return """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                margin: 10px;
                border-radius: 5%;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.4);
                border-radius: 5%;
            }
        """
