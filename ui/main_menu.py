import contextlib

import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.add_student import AddStudent
from ui.courses_tab_widget import CoursesTabWidget
from ui.student import StudentWidget
from ui.student_dialog import StudentDialog
from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.icons import Icons
from utils.school import School
from utils.student import Student


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/main_menu.ui", self)
        self.setWindowTitle("Gradiance")
        self.setWindowIcon(QIcon(Icons.app_icon))
        self.school = School("Pineland")
        self.school.load()
        with contextlib.suppress(IndexError):
            self.last_selected_course: str = self.school.courses[0].name
        self.tabWidget: QTabWidget
        self.load_clicked_events()
        self.load_students()
        self.load_courses()
        self.showMaximized()

    def load_clicked_events(self):
        self.tabWidget.tabBarClicked.connect(self.main_tab_clicked)
        self.pushButton_add_student.clicked.connect(self.add_student)
        self.listWidget_students.itemDoubleClicked.connect(self.open_student_dialog)
        self.actionAdd_Course.triggered.connect(self.add_course)
        self.actionDelete_Course.triggered.connect(self.delete_course)
        self.actionAdd_Student.triggered.connect(self.add_student)
        self.actionDelete_Student.triggered.connect(self.delete_student)

    def open_student_dialog(self):
        student = self.school.get_student_from_name(
            self.listWidget_students.currentItem().text()
        )
        student_dialog = StudentDialog(student, self.school, self)
        student_dialog.show()

    def add_student(self):
        dialog = AddStudent(self)
        if dialog.exec():
            new_student = Student(
                first_name=dialog.get_first_name(),
                middle_name=dialog.get_middle_name(),
                last_name=dialog.get_last_name(),
                gender=dialog.get_gender(),
                birthday=dialog.get_birthday(),
                colony=dialog.get_colony(),
                color=dialog.get_color(),
                notes="",
            )
            self.school.add_student(new_student)
            self.school.save()
        self.load_students()

    def delete_student(self):
        students = [student.name for student in self.school.students]
        item, ok_pressed = QInputDialog.getItem(
            None,
            "Select student",
            "Choose a student to remove:",
            students,
            editable=False,
        )

        if ok_pressed and item:
            student_to_remove = self.school.get_student_from_name(item)
            self.school.remove_student(student_to_remove)
            self.school.save()
            for course in self.school.courses:
                with contextlib.suppress(
                    KeyError, ValueError
                ):  # The student never existed in this course
                    course.remove_student(student_to_remove)
            current_tab = self.tabWidget.tabText(self.tabWidget.currentIndex()).lower()
            if current_tab == "students":
                self.load_students()
            elif current_tab == "courses":
                self.load_courses()

    def load_students(self):
        grouped_data = self._group_students()
        self.clear_layout(self.verticalLayout_students)
        self.listWidget_students.clear()

        for grade_level, students in grouped_data.items():
            group_box = QGroupBox(grade_level, self)
            group_box.setMinimumHeight(350)
            group_box_layout = QVBoxLayout(group_box)
            students_container = QWidget(group_box)
            students_layout = QHBoxLayout(students_container)
            for student in students:
                student_widget = StudentWidget(student, self.school, self)
                student_widget.studentDeleted.connect(self.load_students)
                self.listWidget_students.addItem(student.name)
                students_layout.addWidget(student_widget)
            students_container.setLayout(students_layout)
            scroll_area = QScrollArea(group_box)
            scroll_area.setWidget(students_container)
            group_box_layout.addWidget(scroll_area)
            group_box.setLayout(group_box_layout)
            self.verticalLayout_students.addWidget(group_box)

    def _group_students(self) -> dict:
        grouped_data: dict[str, list[Student]] = {}
        sorted_student_list = sorted(
            self.school.students, key=lambda student: student.get_age()
        )
        for student in reversed(sorted_student_list):
            grouped_data.setdefault(student.get_grade_level(), []).append(student)
        return grouped_data

    def add_course(self):
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter course name:"
        )
        if ok_pressed and text:
            new_course = Course(text)
            self.school.add_course(new_course)
            self.school.save()
            self.load_courses()

    def delete_course(self):
        courses = [course.name for course in self.school.courses]

        item, ok_pressed = QInputDialog.getItem(
            None, "Select course", "Choose a course to delete:", courses, editable=False
        )
        if ok_pressed and item:
            selected_course = self.school.get_course(item)
            self.school.remove_course(selected_course)
            self.school.save()
            self.load_courses()

    def load_courses(self):
        self.clear_layout(self.verticalLayout_courses)
        self.courses_widget = CoursesTabWidget(self.school, self)
        for course in self.school.courses:
            self.courses_widget.add_course(course)
        self.verticalLayout_courses.addWidget(self.courses_widget)
        tab_order = [course.name for course in self.school.courses]
        with contextlib.suppress(ValueError, AttributeError):
            self.courses_widget.setCurrentIndex(
                tab_order.index(self.last_selected_course)
            )
        self.courses_widget.currentChanged.connect(self.courses_tab_changed)
        self.courses_widget.enable_save_tab_order()
        self.courses_widget.load_tab()

    def courses_tab_changed(self):
        self.last_selected_course = self.courses_widget.current_tab()

    def main_tab_clicked(self, index):
        current_tab = self.tabWidget.tabText(index).lower()
        if current_tab == "students":
            self.load_students()
        elif current_tab == "courses":
            self.load_courses()

    def clear_layout(self, layout):
        with contextlib.suppress(AttributeError):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    else:
                        self.clear_layout(item.layout())
