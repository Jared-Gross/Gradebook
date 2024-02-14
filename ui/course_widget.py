import contextlib
import copy

import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QHeaderView,
    QInputDialog,
    QStyledItemDelegate,
    QTableWidget,
    QTabWidget,
    QToolBox,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.assessment_tab_widget import AssessmentTabWidget
from ui.assessment_table_widget import AssessmentTableWidget
from ui.course_summary_widget import CourseSummaryWidget
from ui.student import StudentWidget
from ui.student_dialog import StudentDialog
from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.school import School
from utils.student import Student


class CourseWidget(QWidget):
    def __init__(self, course: Course, school: School, parent=None):
        super(CourseWidget, self).__init__(parent)
        uic.loadUi("ui/course_widget.ui", self)
        self.settings = QSettings("TheCodingJ's", "Gradiance", self)
        self.course: Course = course
        self.school: School = school
        self.parent = parent
        self.assessments: dict[str, QToolBox] = {}
        self.students: dict[str, Student] = {}
        self.last_selected_student: Student = None
        with contextlib.suppress(IndexError):
            self.last_selected_assessment: str = list(self.course.assessments)[0]
        self.last_selected_row: int = 0
        self.last_selected_grading: str = ""
        self.verticalLayout_summary: QVBoxLayout
        self.toolBox: QToolBox
        self.pushButton_add_assessment.clicked.connect(self.add_assessment)
        self.pushButton_remove_assessment.clicked.connect(self.remove_assessment)
        self.listWidget_students.itemSelectionChanged.connect(self.student_changed)
        self.listWidget_students.itemDoubleClicked.connect(self.student_double_clicked)
        self.pushButton_add.clicked.connect(self.add_student)
        self.pushButton_remove.clicked.connect(self.remove_student)
        self.load_students()
        self.listWidget_students.setCurrentRow(self.settings.value("last_selected_student", 0, type=int))
        
        self.load_grading()
        self.treeWidget_grading.header().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.treeWidget_grading.header().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.treeWidget_grading.itemChanged.connect(self.grading_changed)
        self.treeWidget_grading.itemDoubleClicked.connect(self.grading_double_clicked)
        self.toolBox.currentChanged.connect(self.tool_box_change)
        self.toolBox.setCurrentIndex(self.settings.value("last_opened_course_tab", 0, type=int))

    def tool_box_change(self):
        if (
            self.toolBox.itemText(self.toolBox.currentIndex()).lower()
            == "course summary"
        ):
            self.load_summary()
        self.settings.setValue("last_opened_course_tab", self.toolBox.currentIndex())

    def add_student(self):
        _students = [student.name for student in self.school.students]
        students = copy.copy(_students)
        for current_student in self.course.students:
            if current_student.name in _students:
                students.remove(current_student.name)

        item, ok_pressed = QInputDialog.getItem(
            None,
            "Select student",
            "Choose a student to enroll:",
            students,
            editable=False,
        )

        if ok_pressed and item:
            new_student = self.school.get_student_from_name(item)
            self.course.add_student(new_student)
            self.course.sync_assignments(new_student)
            self.school.save()
            self.load_students()
            self.listWidget_students.setCurrentRow(self.settings.value("last_selected_student", 0, type=int))
            

    def remove_student(self):
        students = [student.name for student in self.course.students]
        item, ok_pressed = QInputDialog.getItem(
            None,
            "Select student",
            "Choose a student to remove:",
            students,
            editable=False,
        )

        if ok_pressed and item:
            del self.students[item]
            self.course.remove_student(self.school.get_student_from_name(item))
            self.school.save()
            self.load_students()
            self.listWidget_students.setCurrentRow(self.settings.value("last_selected_student", 0, type=int))

    def student_changed(self):
        with contextlib.suppress(KeyError): # For when a student is removed
            selected_student = self.listWidget_students.currentItem().text()
            self.load_assessments(self.students[selected_student])
            self.last_selected_student = self.students[selected_student]
            self.last_selected_row = self.listWidget_students.currentRow()
            self.settings.setValue("last_selected_student", self.last_selected_row)

    def load_students(self):
        self.listWidget_students.clear()
        for student in self.course.students:
            self.students[student.name] = student
            self.listWidget_students.addItem(student.name)
        if len(list(self.students.keys())) == 1:
            self.listWidget_students.setCurrentRow(0)
        else:
            self.listWidget_students.setCurrentRow(self.settings.value("last_selected_student", 0, type=int))

    def student_double_clicked(self):
        student = self.school.get_student_from_name(
            self.listWidget_students.currentItem().text()
        )
        student_dialog = StudentDialog(student, self.school, self)
        if student_dialog.exec():
            current_tab = self.parent.parent.tabWidget.tabText(
                self.parent.parent.tabWidget.currentIndex()
            ).lower()
            if current_tab == "students":
                self.parent.parent.load_students()
            elif current_tab == "courses":
                self.parent.parent.load_courses()

    def grading_double_clicked(self, item, column):
        self.last_selected_grading = item.text(0)

    def grading_changed(self, item, column):
        if column == 1:
            self.course.grading[item.text(0)] = float(item.text(1))
            self.load_grading()
        else:
            self.course.grading[item.text(0)] = float(item.text(1))
            del self.course.grading[self.last_selected_grading]
            self.course.rename_assessment(self.last_selected_grading, item.text(0))
            self.load_assessments(self.last_selected_student)
        self.school.save()

    def load_grading(self):
        self.treeWidget_grading.blockSignals(True)
        self.treeWidget_grading.clear()
        self.treeWidget_grading.setColumnCount(2)
        self.treeWidget_grading.setHeaderLabels(["Name", "Grade"])
        total: float = 0.0
        for assessment, grade in self.course.grading.items():
            total += grade
            assignments_item = QTreeWidgetItem(
                self.treeWidget_grading, [assessment, str(grade)]
            )
            assignments_item.setFlags(
                assignments_item.flags() | Qt.ItemFlag.ItemIsEditable
            )
        QTreeWidgetItem(self.treeWidget_grading, ["Total", str(total)])
        self.treeWidget_grading.blockSignals(False)

    def add_assessment(self):
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter assessment name:"
        )
        if ok_pressed and text:
            self.course.add_assessment(text)
            self.school.save()
            if self.last_selected_student is not None:
                self.load_assessments(self.last_selected_student)
                self.load_grading()
            self.listWidget_students.setCurrentRow(self.settings.value("last_selected_student", 0, type=int))
            

    def remove_assessment(self):
        assessments = [assessment for assessment in self.course.assessments]

        item, ok_pressed = QInputDialog.getItem(
            None,
            "Select assessment",
            "Choose an assessment to remove:",
            assessments,
            editable=False,
        )

        if ok_pressed and item:
            self.course.remove_assessment(item)
            self.school.save()
            self.load_assessments(self.last_selected_student)
            self.load_grading()

    def load_assessments(self, student: Student = None):
        if student == None:
            student = self.last_selected_student
        self.clear_layout(self.horizontalLayout_3)
        self.assessments.clear()
        self.assessment_tab_box = AssessmentTabWidget(self.school, self.course, self)
        for assessment in self.course.assessments:
            table_widget = AssessmentTableWidget(
                self.school, self.course, student, assessment, self
            )
            self.assessment_tab_box.addTab(table_widget, assessment)
        self.assessment_tab_box.currentChanged.connect(self.assessment_tab_box_changed)
        self.assessment_tab_box.enable_save_tab_order()

        with contextlib.suppress(AttributeError, ValueError):
            self.assessment_tab_box.setCurrentIndex(
                self.assessment_tab_box.get_tab_order().index(
                    self.last_selected_assessment
                )
            )
        self.horizontalLayout_3.addWidget(self.assessment_tab_box)

    def assessment_tab_box_changed(self):
        self.last_selected_assessment = self.assessment_tab_box.tabText(
            self.assessment_tab_box.currentIndex()
        )

    def load_summary(self):
        self.clear_layout(self.verticalLayout_summary)
        summary = CourseSummaryWidget(self.course, self)
        self.verticalLayout_summary.addWidget(summary)

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
