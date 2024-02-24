import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QImage, QPixmap, QColor
from PyQt6.QtWidgets import QMenu, QWidget, QLabel

from ui.student_dialog import StudentDialog
from utils import globals
from utils.assignment import Assignment
from utils.colors import darken_color, lighten_color
from utils.course import Course
from utils.school import School
from utils.student import Student


class StudentWidget(QWidget):
    studentDeleted = pyqtSignal()

    def __init__(self, student: Student, school: School, parent=None):
        super(StudentWidget, self).__init__(parent)
        uic.loadUi("ui/student.ui", self)
        self.student: Student = student
        self.school: School = school
        self.parent = parent
        self.widget: QWidget
        self.label_icon: QLabel
        self.label_name.setText(self.student.name)
        self.label_age.setText(f"{self.student.get_age()} years old")
        self.label_school_stage.setText(
            f"{self.student.get_school_stage()}; {self.student.get_grade_level()}"
        )
        self.label_icon.setPixmap(QPixmap(self.student.icon))
        self.setup_context_menu()
        background_color = QColor(38, 42, 46)
        darker_background_color = darken_color(background_color, 2)
        hover_background_color = lighten_color(background_color, 1.2)
        color = f"border: 2px solid rgb({self.student.color.red()}, {self.student.color.green()}, {self.student.color.blue()});"
        hover_color = lighten_color(self.student.color, 1.2)
        pressed_color = darken_color(self.student.color, 2)
        background = f"background-color: rgb({background_color.red()}, {background_color.green()}, {background_color.blue()});"
        self.pressed_style = (
            "QWidget#widget{"
            + "border: 2px solid rgb(" + f"{self.student.color.red()}, {self.student.color.green()}, {self.student.color.blue()}" + ");"
            + "border-radius: 5px;"
            + "background-color: rgb(" + f"{pressed_color.red()}, {pressed_color.green()}, {pressed_color.blue()}" + "); }"
        )
        self.hover_style = (
            "QWidget#widget:hover{"
            + "border-color: rgb(" + f"{self.student.color.red()}, {self.student.color.green()}, {self.student.color.blue()}" + "); }"
        )
        self.normal_style = "QWidget#widget{" + color + " border-radius: 5px;" + background + "}"
        self.widget.setStyleSheet(self.normal_style + self.hover_style)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.widget.setStyleSheet(self.pressed_style)
            student_dialog = StudentDialog(self.student, self.school, self)
            if student_dialog.exec():
                current_tab = self.parent.tabWidget.tabText(
                    self.parent.tabWidget.currentIndex()
                ).lower()
                if current_tab == "students":
                    self.parent.load_students()
                elif current_tab == "courses":
                    self.parent.load_courses()
            self.widget.setStyleSheet(self.normal_style + self.hover_style)

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def add_to_course(self, course: Course):
        course.add_student(self.student)
        self.school.save()

    def show_context_menu(self, pos):
        # Show the context menu at the specified position
        self.context_menu.exec(self.mapToGlobal(pos))

    def delete(self):
        self.school.remove_student(self.student)
        self.school.save()
        self.studentDeleted.emit()

    def setup_context_menu(self):
        self.context_menu = QMenu(self)
        add_to_course_submenu = QMenu("Add to Course", self)
        for course in self.school.courses:
            course_action = QAction(f"{course.name}", self)
            course_action.triggered.connect(
                lambda _, course=course: self.add_to_course(course)
            )
            add_to_course_submenu.addAction(course_action)
        self.context_menu.addMenu(add_to_course_submenu)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete)
        self.context_menu.addAction(delete_action)

        self.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )  # Qt.ContextMenuPolicy.CustomContextMenu
        self.customContextMenuRequested.connect(self.show_context_menu)
