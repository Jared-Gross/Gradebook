import random

import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import QColorDialog, QDialog

from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.school import School
from utils.student import Student


class AddStudent(QDialog):
    def __init__(self, parent=None):
        super(AddStudent, self).__init__(parent)
        uic.loadUi("ui/add_student.ui", self)
        self.pushButton_set_color.clicked.connect(self.set_color)
        self.color = (
            random.randint(30, 200),
            random.randint(30, 200),
            random.randint(30, 200),
        )
        button_color = QColor(self.color[0], self.color[1], self.color[2])
        self.pushButton_set_color.setStyleSheet(
            f"background-color: {button_color.name()}"
        )
        self.show()

    def get_first_name(self) -> str:
        return self.lineEdit_first_name.text()

    def get_middle_name(self) -> str:
        return self.lineEdit_middle_name.text()

    def get_last_name(self) -> str:
        return self.lineEdit_last_name.text()

    def get_gender(self) -> str:
        return self.comboBox_gender.currentText()

    def get_birthday(self) -> str:
        return self.dateEdit_birthday.date().toString(Qt.DateFormat.ISODate)

    def get_colony(self) -> str:
        return self.lineEdit_colony.text()

    def get_color(self) -> tuple[int, int, int]:
        return self.color

    def set_color(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.color = (color.red(), color.green(), color.blue())
            self.pushButton_set_color.setStyleSheet(f"background-color: {color.name()}")
