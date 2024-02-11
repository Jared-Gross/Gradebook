import contextlib
import copy
import random

import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import QColorDialog, QDialog, QInputDialog, QToolBox, QWidget

from ui.student_summary_widget import StudentSummaryWidget
from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.icons import Icons
from utils.school import School
from utils.student import Student
from utils.generate_student_report import StudentReport


class StudentDialog(QDialog):
    def __init__(self, student: Student, school: School, parent=None):
        super(QDialog, self).__init__(parent)
        uic.loadUi("ui/student_dialog.ui", self)
        self.student = student
        self.school = school
        self.enrolled_courses: dict[str, Course] = {}
        self.color: QColor = self.student.color
        self.pushButton_set_color.setStyleSheet(
            f"background-color: {self.color.name()}"
        )
        self.setWindowTitle(student.name)
        self.lineEdit_first_name.setText(student.first_name)
        self.lineEdit_first_name.textChanged.connect(self.save_changes)
        self.lineEdit_middle_name.setText(student.middle_name)
        self.lineEdit_middle_name.textChanged.connect(self.save_changes)
        self.lineEdit_last_name.setText(student.last_name)
        self.label_name.setText(self.student.name)
        self.lineEdit_last_name.textChanged.connect(self.save_changes)
        self.comboBox_gender.setCurrentText(student.gender)
        self.comboBox_gender.currentTextChanged.connect(self.save_changes)
        self.comboBox_gender.currentTextChanged.connect(self.change_icon)
        self.dateEdit_birthday.setDate(
            QDate.fromString(student.birthday, Qt.DateFormat.ISODate)
        )
        self.dateEdit_birthday.userDateChanged.connect(self.save_changes)

        self.lineEdit_colony.setText(student.colony)
        self.lineEdit_colony.textChanged.connect(self.save_changes)

        self.label_icon.setPixmap(QPixmap(student.icon))

        future = f"Age: {student.get_age()}\n"
        for grade_level in student.get_next_grade_levels():
            future += f"Starting {grade_level[0]} at {grade_level[1]} years old in {grade_level[2]}\n"
        self.label_generated.setText(future)
        self.textEdit_notes.setPlainText(student.notes)
        self.textEdit_notes.textChanged.connect(self.save_changes)
        self.pushButton_add_to_course.clicked.connect(self.add_to_course)
        self.pushButton_remove_from_course.clicked.connect(self.remove_from_course)
        self.pushButton_set_color.clicked.connect(self.set_color)
        self.pushButton_generate_student_summary.clicked.connect(
            self.generate_student_summary
        )
        self.show()
        self.resize(800, 550)
        self.load_courses()
        self.load_summary()

    def change_icon(self):
        if self.comboBox_gender.currentText() == "Male":
            self.student.icon = random.choice(Icons.male_icons)
        else:
            self.student.icon = random.choice(Icons.female_icons)
        self.label_icon.setPixmap(QPixmap(self.student.icon))
        self.save_changes()

    def save_changes(self):
        self.student.first_name = self.lineEdit_first_name.text()
        self.student.middle_name = self.lineEdit_middle_name.text()
        self.student.last_name = self.lineEdit_last_name.text()
        self.student.gender = self.comboBox_gender.currentText()
        self.student.birthday = self.dateEdit_birthday.date().toString(
            Qt.DateFormat.ISODate
        )
        self.student.colony = self.lineEdit_colony.text()
        self.student.notes = self.textEdit_notes.toPlainText()
        self.student.color = self.color
        self.student.name = (
            f"{self.lineEdit_first_name.text()} {self.lineEdit_last_name.text()}"
        )
        self.label_name.setText(self.student.name)
        future = f"Age: {self.student.get_age()}\n"
        for grade_level in self.student.get_next_grade_levels():
            future += f"Starting {grade_level[0]} at {grade_level[1]} years old in {grade_level[2]}\n"
        self.label_generated.setText(future)
        self.school.save()

    def set_color(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.color = QColor(color.red(), color.green(), color.blue())
            self.pushButton_set_color.setStyleSheet(f"background-color: {color.name()}")
            self.save_changes()

    def add_to_course(self):
        _courses = [course.name for course in self.school.courses]
        courses = copy.copy(_courses)
        for current_course in list(self.enrolled_courses.keys()):
            if current_course in _courses:
                courses.remove(current_course)

        item, ok_pressed = QInputDialog.getItem(
            None, "Select course", "Choose a course to enroll:", courses, editable=False
        )

        if ok_pressed and item:
            selected_course = self.school.get_course(item)
            selected_course.add_student(self.student)
            self.school.save()
            self.load_courses()
            self.load_summary()

    def remove_from_course(self):
        courses = list(self.enrolled_courses.keys())
        item, ok_pressed = QInputDialog.getItem(
            None, "Select course", "Choose a course to remove:", courses, editable=False
        )

        if ok_pressed and item:
            self.enrolled_courses[item].remove_student(self.student)
            self.school.save()
            self.load_courses()
            self.load_summary()

    def generate_student_summary(self):
        summary = StudentReport(self.school, self.student)
        summary.generate()

    def load_summary(self):
        self.clear_layout(self.verticalLayout_summary)
        courses_tool_box = QToolBox(self)
        courses_tool_box.setMinimumHeight(len(list(self.enrolled_courses.keys()))*40)
        for course in self.enrolled_courses:
            summary_widget = StudentSummaryWidget(
                self.enrolled_courses[course], self.student, courses_tool_box
            )
            courses_tool_box.addItem(summary_widget, course)

        self.verticalLayout_summary.addWidget(courses_tool_box)

    def load_courses(self):
        self.listWidget_courses.clear()
        self.enrolled_courses.clear()
        counter: int = 0
        for course in self.school.courses:
            if self.student in course.students:
                self.listWidget_courses.addItem(f"{str(counter+1)}. {course.name}")
                self.enrolled_courses[course.name] = course
                counter += 1

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

    def closeEvent(self, event):
        self.accept()
