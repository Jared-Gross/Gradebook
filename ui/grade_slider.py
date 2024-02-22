import contextlib

from PyQt6 import uic
from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QRegularExpressionValidator, QResizeEvent
from PyQt6.QtWidgets import QLabel, QWidget

from ui.grade_letters import GradeLetters
from utils import globals
from utils.assignment import Assignment
from utils.letter_grade import get_letter_grade
from utils.school import School


class GradeSlider(QWidget):
    def __init__(self, school: School, assignment: Assignment, parent=None):
        super(GradeSlider, self).__init__(parent)
        uic.loadUi("ui/grade_slider.ui", self)
        self.school = school
        self.assignment = assignment
        self.horizontalSlider.setMaximum(int(self.assignment.template.worth))
        self.horizontalSlider.wheelEvent = lambda event: event.ignore()
        self.lineEdit_input.setText(
            f"{self.assignment.score}/{self.assignment.template.worth}"
        )
        regex = QRegularExpression("[-]?[0-9]+[,.]?[0-9]*([\/][0-9]+[,.]?[0-9]*)*")
        validator = QRegularExpressionValidator(regex)
        self.lineEdit_input.setValidator(validator)
        self.doubleSpinBox_percentage.wheelEvent = lambda event: event.ignore()
        try:
            self.doubleSpinBox_percentage.setValue(
                self.assignment.score / self.assignment.template.worth * 100
            )
        except ZeroDivisionError:
            self.doubleSpinBox_percentage.setValue(0.0)
        self.horizontalSlider.setValue(int(self.assignment.score))
        self.doubleSpinBox_percentage.valueChanged.connect(self.percentage_change)
        self.horizontalSlider.valueChanged.connect(self.slider_changed)
        self.lineEdit_input.editingFinished.connect(self.input_grade_changed)
        self.widget_letters: QWidget
        grade_letters = GradeLetters(self)
        self.horizontalLayout_2.addWidget(grade_letters)
        self.update_letter_grade()

    def percentage_change(self):
        with contextlib.suppress(TypeError):
            self.horizontalSlider.disconnect()
        self.horizontalSlider.setValue(int(self.get_percentage()))
        self.assignment.score = int(self.get_percentage())
        self.lineEdit_input.setText(
            f"{int(self.get_percentage())}/{self.assignment.template.worth}"
        )
        self.horizontalSlider.valueChanged.connect(self.slider_changed)
        self.update_letter_grade()

    def input_grade_changed(self):
        new_grade = self.lineEdit_input.text().strip()
        if "/" not in new_grade:
            worth = 100
        else:
            if new_grade.split("/")[-1] == "":
                return
            worth = float(new_grade.split("/")[-1])

        score = float(new_grade.split("/")[0])

        if worth == 0:
            return

        self.assignment.score = score
        self.assignment.template.worth = worth

        with contextlib.suppress(TypeError):
            self.doubleSpinBox_percentage.disconnect()
        self.doubleSpinBox_percentage.setValue(score / worth * 100)
        with contextlib.suppress(TypeError):
            self.horizontalSlider.disconnect()
        self.horizontalSlider.setMaximum(int(worth))
        self.horizontalSlider.setValue(int(score))
        self.horizontalSlider.valueChanged.connect(self.slider_changed)
        self.doubleSpinBox_percentage.valueChanged.connect(self.percentage_change)
        self.update_letter_grade()

    def slider_changed(self):
        with contextlib.suppress(TypeError):
            self.doubleSpinBox_percentage.disconnect()
            self.lineEdit_input.disconnect()
        self.lineEdit_input.setText(
            f"{self.horizontalSlider.value()}/{self.get_worth()}"
        )
        self.doubleSpinBox_percentage.setValue(
            (self.horizontalSlider.value() / self.get_worth()) * 100
        )
        self.assignment.score = self.horizontalSlider.value()
        self.doubleSpinBox_percentage.valueChanged.connect(self.percentage_change)
        self.lineEdit_input.editingFinished.connect(self.input_grade_changed)
        self.update_letter_grade()

    def update_letter_grade(self):
        self.label_letter_grade.setText(get_letter_grade(self.get_percentage()))
        self.assignment.template.worth = self.get_worth()
        self.assignment.score = self.get_score()
        self.school.save()

    def get_score(self) -> float:
        return self.assignment.score

    def get_worth(self) -> float:
        return self.assignment.template.worth

    def get_percentage(self) -> float:
        return self.doubleSpinBox_percentage.value()
