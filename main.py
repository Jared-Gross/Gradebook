import sys

from PyQt6.QtWidgets import QApplication

from ui.main_menu import MainMenu
from utils import globals

globals.initialize()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu(app)
    window.show()
    app.exec()
