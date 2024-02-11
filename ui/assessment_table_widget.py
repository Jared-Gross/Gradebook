import contextlib

import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QAbstractScrollArea,
    QHeaderView,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolBox,
    QWidget,
    QInputDialog,
)

from ui.grade_slider import GradeSlider
from ui.student import StudentWidget
from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.school import School
from utils.student import Student

from functools import partial


class AssessmentTableWidget(QTableWidget):
    def __init__(
        self,
        school: School,
        course: Course,
        student: Student,
        assessment: str,
        parent=None,
    ):
        super(AssessmentTableWidget, self).__init__(parent)
        self.school = school
        self.course = course
        self.student = student
        self.assessment: str = assessment
        self.cellChanged.connect(self.cell_changed)
        self.cellDoubleClicked.connect(self.cell_double_clicked)
        self.table: dict[str, GradeSlider] = {}
        self.last_selected_assignment: str = ""
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.load_coursework()
        self.setup_context_menu()

    def cell_double_clicked(self, row: int, column: int):
        if column != 0:
            return
        with contextlib.suppress(AttributeError):
            self.last_selected_assignment = self.item(row, 0).text()

    def cell_changed(self, changed_row: int, changed_column: int):
        if changed_column != 0:
            return
        try:
            if self.item(changed_row, 0).text() == "":
                with contextlib.suppress(KeyError):
                    self.course.remove_coursework(
                        self.assessment,
                        self.student,
                        self.table[self.last_selected_assignment].assignment,
                    )
                    self.load_coursework()
            else:
                self.table[self.last_selected_assignment].assignment.name = self.item(
                    changed_row, 0
                ).text()
            self.school.save()
        except KeyError:
            assignment_name = self.item(changed_row, 0).text()
            if assignment_name == "":
                return
            self.course.add_coursework(
                self.assessment, self.student, Assignment(assignment_name)
            )
            self.school.save()
            self.load_coursework()

    def load_coursework(self):
        self.blockSignals(True)
        self.clear()
        self.table.clear()
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Name", "Grade"])
        self.setRowCount(50)
        self.horizontalHeader().setStretchLastSection(True)
        for row, coursework in enumerate(
            self.course.assessments[self.assessment][self.student]
        ):
            self.setItem(row, 0, QTableWidgetItem(coursework.name))
            grade_slider = GradeSlider(self.school, coursework, self)
            self.table[coursework.name] = grade_slider
            self.setCellWidget(row, 1, grade_slider)
        self.resizeColumnsToContents()
        header = self.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.blockSignals(False)

    def show_context_menu(self, pos):
        self.context_menu.exec(self.mapToGlobal(pos))

    def delete(self):
        selected_items = self.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()
            assignment_to_delete = self.item(selected_row, 0).text()
            self.course.remove_coursework(
                self.assessment, self.student, assignment_to_delete
            )
            self.load_coursework()

    def quick_add(self, number_of_elemets):
        text, ok_pressed = QInputDialog.getText(
            None,
            f"Input Dialog for {number_of_elemets} elements",
            "Enter element name:",
            text="Element",
        )
        if ok_pressed and text:
            for i in range(number_of_elemets):
                self.course.add_coursework(
                    self.assessment, self.student, Assignment(f"{text} {i+1}")
                )
            self.school.save()
            self.load_coursework()

    def setup_context_menu(self):
        self.context_menu = QMenu(self)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete)
        self.context_menu.addAction(delete_action)

        quick_add_menu = QMenu("Quick Add", self)
        for i in range(15):
            quick_add = QAction(f"{i+1} elements", quick_add_menu)
            quick_add.triggered.connect(partial(self.quick_add, i + 1))
            quick_add_menu.addAction(quick_add)

        self.context_menu.addMenu(quick_add_menu)

        self.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )  # Qt.ContextMenuPolicy.CustomContextMenu
        self.customContextMenuRequested.connect(self.show_context_menu)
