import sys
from PyQt5.QtWidgets import QApplication
from app.overlay import Overlay

def main():
    app = QApplication(sys.argv)
    overlay = Overlay()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
