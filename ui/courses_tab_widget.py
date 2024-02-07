import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QInputDialog, QTabWidget, QWidget

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
        self.courses: dict[Course, QWidget] = {}
        self.school = school
        self.setMovable(True)
        self.tabBarDoubleClicked.connect(self.rename_tab)

    def rename_tab(self):
        old_name = self.current_tab()
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter course name:", text=old_name
        )
        if ok_pressed and text:
            for course in self.school.courses:
                if course.name == old_name:
                    course.name = text
                    self.school.save()
                    break
            self.parent.last_selected_course = text
            self.parent.load_courses()

    def enable_save_tab_order(self):
        self.currentChanged.connect(self.save_tab_order)

    def current_tab(self) -> str:
        return self.tabText(self.currentIndex())

    def add_course(self, course: Course):
        course_widget = CourseWidget(course, self.school, self)
        self.addTab(course_widget, course.name)
        self.courses[course] = course_widget

    def get_tab_order(self) -> list[str]:
        return [self.tabText(i) for i in range(self.count())]

    def save_tab_order(self):
        tab_order = self.get_tab_order()
        courses_order: list[Course] = []
        self.school.courses
        for tab in tab_order:
            for course in self.school.courses:
                if tab == course.name:
                    courses_order.append(course)
        self.school.courses = courses_order
        self.school.save()
