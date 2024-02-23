import contextlib
import os
from functools import partial

import qt_material
import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import QSettings, Qt, QFile, QTextStream
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QMainWindow,
    QMenu,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from ui.about_dialog import AboutDialog
from ui.add_student import AddStudent
from ui.courses_list_widget import CoursesListWidget
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
    def __init__(self, app: QApplication):
        super(QMainWindow, self).__init__()
        uic.loadUi("ui/main_menu.ui", self)
        self.app = app
        self.settings = QSettings("TheCodingJ's", "Gradiance", self)
        self.setWindowIcon(QIcon(Icons.app_icon))
        try:
            self.school = School(
                self.settings.value(
                    "last_opened_school", os.listdir("database")[0], type=str
                )
            )
            self.school.load()
        except IndexError:  # No database has been made
            with contextlib.suppress(AttributeError):
                self.add_school()
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
        self.load_themes_menu()
        self.change_theme(
            self.settings.value(f"{self.school.name} - theme", "dark_teal.xml")
        )

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
        self.actionAbout.triggered.connect(self.show_about)
        self.actionAbout_Qt.triggered.connect(QApplication.aboutQt)

    def load_themes_menu(self):
        self.menuTheme.clear()
        for theme in qt_material.list_themes():
            action = QAction(theme, self)
            action.setCheckable(True)
            action.setChecked(False)
            if (
                self.settings.value(f"{self.school.name} - theme", "dark_teal.xml")
                == theme
            ):
                action.setChecked(True)
            action.triggered.connect(partial(self.change_theme, theme))
            self.menuTheme.addAction(action)

    def change_theme(self, theme: str):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.settings.setValue(f"{self.school.name} - theme", theme)
        qt_material.apply_stylesheet(self.app, theme)
        if "dark" in theme:
            self.setStyleSheet(
                "QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox{color: #eeeeee;}"
            )
        else:
            self.setStyleSheet(
                "QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox{color: #333333;}"
            )
        self.load_themes_menu()
        with contextlib.suppress(AttributeError):  # It is not init'd yet
            self.courses_widget.course_widget.course_summary.load_graphs()
        QApplication.restoreOverrideCursor()

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
            courses_order.extend(
                course for course in self.school.courses if tab == course.name
            )
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
        current_item = (
            0
            if self.last_selected_course is None
            else courses.index(self.last_selected_course)
        )
        item, ok_pressed = QInputDialog.getItem(
            None,
            "Select course",
            "Choose a course to delete:",
            courses,
            current_item,
            editable=False,
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
        with contextlib.suppress(AttributeError):  # No school exists yet
            self.school.save()
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter school name:"
        )
        if ok_pressed and text:
            self.school = School(text)
            self.school.load()
            self.settings.setValue(f"{self.school.name} - theme", "dark_teal.xml")
            self.load_themes_menu()
            self.load_schools()
            self.load_courses()

    def delete_school(self):
        self.school.save()
        schools = os.listdir("database")
        current_item = schools.index(self.school.name)

        item, ok_pressed = QInputDialog.getItem(
            None,
            "Select course",
            "Choose a course to delete:",
            schools,
            current_item,
            editable=False,
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
        self.change_theme(
            self.settings.value(f"{self.school.name} - theme", "dark_teal.xml")
        )
        self.load_themes_menu()
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

    def show_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.show()

    def show_file_contents(self, filename):
        file = QFile(filename)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            contents = stream.readAll()
            QMessageBox.information(self, "File Contents", contents)
            file.close()
        else:
            QMessageBox.warning(self, "Error", f"Failed to open {filename}")

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
