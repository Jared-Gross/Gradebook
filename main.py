import sys

from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from ui.main_menu import MainMenu
from utils import globals

globals.initialize()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_teal.xml")
    window = MainMenu()
    window.setStyleSheet(
        "QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox{color: white;}"
    )
    window.show()
    app.exec()
