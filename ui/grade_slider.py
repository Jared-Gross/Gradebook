import contextlib

import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolBox,
    QWidget,
)

from ui.student import StudentWidget
from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.school import School
from utils.student import Student


class GradeSlider(QWidget):
    def __init__(self, school: School, assignment: Assignment, parent=None):
        super(GradeSlider, self).__init__(parent)
        uic.loadUi("ui/grade_slider.ui", self)
        self.school = school
        self.assignment = assignment
        self.doubleSpinBox_score.setValue(assignment.score)
        self.doubleSpinBox_worth.setValue(int(assignment.worth))
        self.horizontalSlider.setMaximum(int(assignment.worth))
        self.doubleSpinBox_worth.wheelEvent = lambda event: event.ignore()
        self.horizontalSlider.wheelEvent = lambda event: event.ignore()
        self.doubleSpinBox_score.wheelEvent = lambda event: event.ignore()
        self.doubleSpinBox_percentage.wheelEvent = lambda event: event.ignore()
        try:
            self.doubleSpinBox_percentage.setValue(
                assignment.score / assignment.worth * 100
            )
        except ZeroDivisionError:
            self.doubleSpinBox_percentage.setValue(0.0)
        self.horizontalSlider.setValue(int(assignment.score))
        self.update_letter_grade()

        self.doubleSpinBox_percentage.valueChanged.connect(self.percentage_change)
        self.doubleSpinBox_score.valueChanged.connect(self.score_changed)
        self.doubleSpinBox_worth.valueChanged.connect(self.worth_changed)
        self.horizontalSlider.valueChanged.connect(self.slider_changed)

    def percentage_change(self):
        with contextlib.suppress(TypeError):
            self.horizontalSlider.disconnect()
        self.horizontalSlider.setValue(int(self.get_percentage()))
        self.doubleSpinBox_score.setValue(
            self.get_worth() * self.get_percentage() / 100
        )
        self.horizontalSlider.valueChanged.connect(self.slider_changed)
        self.update_letter_grade()

    def score_changed(self):
        # self.doubleSpinBox_percentage.disconnect()
        # self.horizontalSlider.disconnect()
        self.horizontalSlider.setValue(int(self.get_score()))
        with contextlib.suppress(ZeroDivisionError):
            self.doubleSpinBox_percentage.setValue(
                (self.get_score() / self.get_worth()) * 100
            )
        # self.doubleSpinBox_percentage.valueChanged.connect(self.percentage_change)
        # self.horizontalSlider.valueChanged.connect(self.slider_changed)
        self.assignment.score = self.get_score()
        self.update_letter_grade()

    def worth_changed(self):
        with contextlib.suppress(TypeError):
            self.doubleSpinBox_percentage.disconnect()
            self.horizontalSlider.disconnect()
        self.doubleSpinBox_percentage.setValue(
            (self.get_score() / self.get_worth()) * 100
        )
        self.horizontalSlider.setValue(int(self.get_percentage()))
        # self.doubleSpinBox_score.setMaximum(float(self.get_worth()))
        self.horizontalSlider.setMaximum(int(self.get_worth()))
        self.doubleSpinBox_percentage.valueChanged.connect(self.percentage_change)
        self.horizontalSlider.valueChanged.connect(self.slider_changed)
        self.assignment.worth = self.get_worth()
        self.update_letter_grade()

    def slider_changed(self):
        with contextlib.suppress(TypeError):
            self.doubleSpinBox_percentage.disconnect()
            self.doubleSpinBox_score.disconnect()
        self.doubleSpinBox_percentage.setValue(
            (self.horizontalSlider.value() / self.get_worth()) * 100
        )
        self.doubleSpinBox_score.setValue(
            self.get_worth() * self.get_percentage() / 100
        )
        self.doubleSpinBox_percentage.valueChanged.connect(self.percentage_change)
        self.doubleSpinBox_score.valueChanged.connect(self.score_changed)
        self.update_letter_grade()

    def update_letter_grade(self):
        self.label_letter_grade.setText(self.get_letter_grade())
        self.assignment.worth = self.get_worth()
        self.assignment.score = self.get_score()
        self.school.save()

    def get_score(self) -> float:
        return self.doubleSpinBox_score.value()

    def get_worth(self) -> float:
        return self.doubleSpinBox_worth.value()

    def get_percentage(self) -> float:
        return self.doubleSpinBox_percentage.value()

    def get_letter_grade(self) -> str:
        percentage = self.get_percentage()

        # Define grade ranges and their corresponding letter grades
        grade_ranges = [
            (90, "A+"),
            (85, "A"),
            (80, "A-"),
            (77, "B+"),
            (73, "B"),
            (70, "B-"),
            (69, "C+"),
            (63, "C"),
            (60, "C-"),
            (50, "D"),
            (0, "F"),
        ]
        for min_percentage, letter_grade in grade_ranges:
            if percentage >= min_percentage:
                return letter_grade

        return "F"
