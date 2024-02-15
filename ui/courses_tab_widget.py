import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QInputDialog,
    QTabWidget,
    QWidget,
    QTabBar,
    QStyle,
    QStyleOptionTab,
)

from ui.course_widget import CourseWidget
from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.school import School
from utils.student import Student


class CoursesTabWidget(QTabWidget):
    def __init__(self, school: School, parent=None):
        super(CoursesTabWidget, self).__init__(parent)
        self.parent = parent
        self.courses: dict[str, Course] = {}
        self.school = school
        self.tabBar().hide()

    def load_tab(self):
        course_name = self.current_tab()
        try:
            course_widget = CourseWidget(self.courses[course_name], self.school, self)
        except KeyError:  # No courses have been added yet
            return
        self.blockSignals(True)
        self.insertTab(self.currentIndex(), course_widget, course_name)
        # NOTE With out this if statement you cannot select the last tab
        if self.currentIndex() == self.count() - 1:
            self.removeTab(self.currentIndex())
            self.setCurrentIndex(self.currentIndex() + 1)
        else:
            self.removeTab(self.currentIndex())
            self.setCurrentIndex(self.currentIndex() - 1)
        self.blockSignals(False)

    def enable(self):
        self.currentChanged.connect(self.load_tab)

    def current_tab(self) -> str:
        return self.tabText(self.currentIndex())

    def add_course(self, course: Course):
        self.addTab(QWidget(self), course.name)
        self.courses[course.name] = course

    def get_tab_order(self) -> list[str]:
        return [self.tabText(i) for i in range(self.count())]
