import contextlib

import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QAbstractScrollArea, QHeaderView, QInputDialog,
                             QMenu, QTableWidget, QTableWidgetItem, QTabWidget,
                             QToolBox, QWidget)

from ui.grade_slider import GradeSlider
from ui.student import StudentWidget
from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.school import School
from utils.student import Student


class AssessmentTabWidget(QTabWidget):
    def __init__(
        self,
        school: School,
        course: Course,
        parent=None,
    ):
        super(AssessmentTabWidget, self).__init__(parent)
        self.school = school
        self.course = course
        self.parent = parent
        self.setMovable(True)
        self.setTabShape(QTabWidget.TabShape.Triangular)
        self.tabBarDoubleClicked.connect(self.rename_tab)

    def rename_tab(self):
        tab_order = self.get_tab_order()
        old_name = self.current_tab()
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter assessment name:", text=old_name
        )
        if ok_pressed and text:
            for assessment in self.course.assessments:
                if assessment == old_name:
                    assessment_grading = self.course.grading[old_name]
                    del self.course.grading[old_name]
                    self.course.grading[text] = assessment_grading
                    self.course.rename_assessment(old_name, text)
                    self.school.save()
                    break
            self.parent.last_selected_assessment = text
            self.parent.load_assessments()
            self.parent.load_grading()

    def enable_save_tab_order(self):
        self.currentChanged.connect(self.save_tab_order)

    def current_tab(self) -> str:
        return self.tabText(self.currentIndex())

    def get_tab_order(self) -> list[str]:
        return [self.tabText(i) for i in range(self.count())]

    def save_tab_order(self):
        tab_order = self.get_tab_order()
        new_order: dict[str, Student] = {}
        for tab in tab_order:
            for assessment in self.course.assessments:
                if tab == assessment:
                    new_order[assessment] = self.course.assessments[assessment]
        self.course.assessments = new_order
        self.school.save()
