import contextlib
import os
from functools import partial

import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon, QAction
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
    QListWidget,
    QMenu,
)

from ui.add_student import AddStudent
from ui.courses_tab_widget import CoursesTabWidget
from ui.student import StudentWidget
from ui.student_dialog import StudentDialog
from ui.courses_list_widget import CoursesListWidget
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
        self.settings = QSettings("TheCodingJ's", "Gradiance", self)
        self.setWindowIcon(QIcon(Icons.app_icon))
        self.school = School(
            self.settings.value(
                "last_opened_school", os.listdir("database")[0], type=str
            )
        )
        self.school.load()
        try:
            self.last_selected_course: str = self.settings.value(
                f"{self.school.name} - last_selected_course",
                self.school.courses[0].name,
                type=str,
            )
        except IndexError:
            self.last_selected_course: str = ""
        self.tabWidget: QTabWidget
        self.tabWidget.setCurrentIndex(
            self.settings.value("last_opened_tab", 0, type=int)
        )
        self.listWidget_students: QListWidget
        self.listWidget_courses = CoursesListWidget(self.school, self)
        self.courses_list_widget_layout.addWidget(self.listWidget_courses)
        self.load_clicked_events()
        self.load_schools()
        self.load_students()
        self.load_courses()
        self.showMaximized()

    def load_clicked_events(self):
        self.tabWidget.tabBarClicked.connect(self.main_tab_clicked)
        self.pushButton_add_student.clicked.connect(self.add_student)
        self.listWidget_students.itemDoubleClicked.connect(self.open_student_dialog)
        self.listWidget_courses.itemClicked.connect(
            self.list_widget_courses_selection_changed
        )
        self.listWidget_courses.itemDoubleClicked.connect(self.rename_tab)
        self.listWidget_courses.dropEventOccurred.connect(self.save_courses_tab_order)
        self.actionAdd_Course.triggered.connect(self.add_course)
        self.pushButton_add_course.clicked.connect(self.add_course)
        self.actionDelete_Course.triggered.connect(self.delete_course)
        self.pushButton_remove_course.clicked.connect(self.delete_course)
        self.actionAdd_Student.triggered.connect(self.add_student)
        self.actionDelete_Student.triggered.connect(self.delete_student)
        self.actionAdd_New_School.triggered.connect(self.add_school)
        self.actionRemove_School.triggered.connect(self.delete_school)

    def open_student_dialog(self):
        student = self.school.get_student_from_name(
            self.listWidget_students.currentItem().text()
        )
        student_dialog = StudentDialog(student, self.school, self)
        student_dialog.show()

    def list_widget_courses_selection_changed(self):
        tab_order = self.courses_widget.get_tab_order()
        self.courses_widget.setCurrentIndex(
            tab_order.index(self.listWidget_courses.currentItem().text())
        )
        self.last_selected_course = self.courses_widget.current_tab()
        self.settings.setValue(
            f"{self.school.name} - last_selected_course", self.last_selected_course
        )

    def rename_tab(self):
        old_name = self.listWidget_courses.currentItem().text()
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter course name:", text=old_name
        )
        if ok_pressed and text:
            for course in self.school.courses:
                if course.name == old_name:
                    course.name = text
                    self.school.save()
                    break
            self.last_selected_course = text
            self.settings.setValue(
                f"{self.school.name} - last_selected_course", self.last_selected_course
            )
            self.load_courses()

    def save_courses_tab_order(self):
        tab_order = [
            self.listWidget_courses.item(i).text()
            for i in range(self.listWidget_courses.count())
        ]
        courses_order: list[Course] = []
        for tab in tab_order:
            for course in self.school.courses:
                if tab == course.name:
                    courses_order.append(course)
        self.school.courses = courses_order
        self.school.save()

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
        self.listWidget_courses.clear()
        self.courses_widget = CoursesTabWidget(self.school, self)
        for course in self.school.courses:
            self.courses_widget.add_course(course)
            self.listWidget_courses.addItem(course.name)
        self.verticalLayout_courses.addWidget(self.courses_widget)
        tab_order = [course.name for course in self.school.courses]
        self.courses_widget.enable()
        try:
            self.courses_widget.setCurrentIndex(
                tab_order.index(
                    self.settings.value(
                        f"{self.school.name} - last_selected_course", "", type=str
                    )
                )
            )
            self.listWidget_courses.setCurrentRow(
                tab_order.index(
                    self.settings.value(
                        f"{self.school.name} - last_selected_course", "", type=str
                    )
                )
            )
        except (AttributeError, ValueError):
            self.courses_widget.setCurrentIndex(0)
            self.listWidget_courses.setCurrentRow(0)
        self.courses_widget.load_tab()

    def add_school(self):
        self.school.save()
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter school name:"
        )
        if ok_pressed and text:
            self.school = School(text)
            self.school.load()
            self.load_schools()
            self.load_courses()

    def delete_school(self):
        self.school.save()
        schools = os.listdir("database")

        item, ok_pressed = QInputDialog.getItem(
            None, "Select course", "Choose a course to delete:", schools, editable=False
        )
        if ok_pressed and item:
            schools.remove(item)
            if self.school.name == item:
                self.school = School(schools[0])
                self.school.save()
            self.load_schools()
            os.remove(f"{globals.database_location}/{item}")

    def load_school(self, school_name: str):
        self.settings.setValue("last_opened_school", school_name)
        self.school.save()
        self.school = School(school_name)
        self.school.load()
        self.load_students()
        self.load_courses()

    def load_schools(self):
        self.menuLoad_School.clear()
        for school in os.listdir("database"):
            action = QAction(school, self.menuLoad_School)
            action.triggered.connect(partial(self.load_school, school))
            self.menuLoad_School.addAction(action)

    def main_tab_clicked(self, index: int):
        self.settings.setValue("last_opened_tab", index)
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
