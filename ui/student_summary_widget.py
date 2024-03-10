import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHeaderView,
    QTableWidget,
    QTabWidget,
    QToolBox,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.letter_grade import get_letter_grade
from utils.school import School
from utils.student import Student


class StudentSummaryWidget(QTreeWidget):
    def __init__(self, course: Course, student: Student, parent=None):
        super(StudentSummaryWidget, self).__init__(parent)
        self.course = course
        self.student = student
        self.setColumnCount(2)
        self.setHeaderLabels(["Name", "Score", "%", "Wght", "Ltr Grd"])
        self.load_summary()
        self.setVerticalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)

    def load_summary(self):
        grand_total_score = 0.0
        grand_total_worth = 0.0
        grand_total_weighted_score = 0.0
        grand_total_weight = 0.0
        for assessment in self.course.assessments:
            total_score = 0.0
            total_worth = 0.0
            assessment_weight = self.course.grading[assessment]
            grand_total_weight += assessment_weight
            total_assignments = len(self.course.assessments[assessment][self.student])
            assessment_item = QTreeWidgetItem(self, [assessment, "", "", "", ""])
            for assignment in self.course.assessments[assessment][self.student]:
                total_score += assignment.score
                total_worth += assignment.template.worth
                if assignment.template.worth != 0:
                    weighted_percentage = assignment.score / assignment.template.worth
                    assignment_item = QTreeWidgetItem(
                        assessment_item,
                        [
                            assignment.template.name,
                            f"{round(assignment.score, 2)}/{round(assignment.template.worth, 2)}",
                            f"{round((weighted_percentage)*100, 2)}%",
                            f"{round((assessment_weight/total_assignments)*(weighted_percentage), 2)}/{round(assessment_weight/total_assignments,2)}",
                            assignment.get_letter_grade(),
                        ],
                    )
                else:
                    assignment_item = QTreeWidgetItem(
                        assessment_item,
                        [
                            assignment.template.name,
                            f"{round(assignment.score, 2)}/{round(assignment.template.worth, 2)}",
                            f"0.0%",
                            f"0.0/{round(assessment_weight/total_assignments,2)}",
                            assignment.get_letter_grade(),
                        ],
                    )
                assessment_item.addChild(assignment_item)

            # Set the total grade for the assessment
            total_grade_percentage = (
                (total_score / total_worth) * 100 if total_worth != 0 else 0.0
            )
            weighted_score = assessment_weight * total_grade_percentage / 100
            assessment_item.setData(
                1, 0, f"{round(total_score, 2)}/{round(total_worth, 2)}"
            )
            assessment_item.setData(2, 0, f"{round(total_grade_percentage, 2)}%")
            try:
                assessment_item.setData(
                    3, 0, f"{round(weighted_score, 2)}/{round(assessment_weight, 2)}"
                )
            except ZeroDivisionError:
                assessment_item.setData(3, 0, "0.0%")
            grand_total_score += total_score
            grand_total_worth += total_worth
            grand_total_weighted_score += weighted_score
        grand_total_grade_percentage = (
            (grand_total_score / grand_total_worth) * 100
            if grand_total_worth != 0
            else 0.0
        )
        total_item = QTreeWidgetItem(self, ["Total", "", "", ""])
        total_item.setData(
            1, 0, f"{round(grand_total_score, 2)}/{round(grand_total_worth, 2)}"
        )
        total_item.setData(2, 0, f"{round(grand_total_grade_percentage, 2)}%")
        try:
            total_item.setData(
                3, 0, f"{round(grand_total_weighted_score/grand_total_weight*100, 2)}%"
            )
        except ZeroDivisionError:
            total_item.setData(3, 0, "0.00%")
        try:
            total_item.setData(
                4,
                0,
                f"{get_letter_grade(grand_total_weighted_score/grand_total_weight*100)}",
            )
        except ZeroDivisionError:
            total_item.setData(4, 0, "0.00")
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
