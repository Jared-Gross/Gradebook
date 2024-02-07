import os

from utils import globals
from utils.assignment import Assignment
from utils.student import Student


class Course:
    def __init__(self, name: str):
        self.name: str = name
        self.grading: dict[str, float] = {}
        self.students: list[Student] = []
        self.assessments: dict[str, dict[Student, list[Assignment]]] = {}
        newpath = f"{globals.database_location}/{self.name}"
        if not os.path.exists(newpath):
            os.makedirs(newpath)

    def add_student(self, student: Student):
        self.students.append(student)
        for assessment in self.assessments:
            self.assessments[assessment][student] = []
            newpath = f"{globals.database_location}/{self.name}/{student.first_name} {student.last_name}/{assessment}"
            if not os.path.exists(newpath):
                os.makedirs(newpath)

    def remove_student(self, student: Student):
        self.students.remove(student)
        for assessment in self.assessments:
            del self.assessments[assessment][student]

    def add_assessment(self, name: str):
        self.assessments[name] = {}
        self.grading.setdefault(name, 0.0)
        for student in self.students:
            self.assessments[name].setdefault(student, [])
        newpath = f"{globals.database_location}/{self.name}/Assessments/{name}"
        if not os.path.exists(newpath):
            os.makedirs(newpath)

    def rename_assessment(self, old_name: str, new_name: str):
        self.assessments[new_name] = self.assessments[old_name]
        del self.assessments[old_name]

    def remove_assessment(self, name: str):
        del self.assessments[name]
        del self.grading[name]

    def add_coursework(self, assessment: str, student: Student, assignment: Assignment):
        self.assessments[assessment][student].append(assignment)

    def remove_coursework(
        self, assessment: str, student: Student, assignment_to_delete: Assignment
    ):
        if isinstance(assignment_to_delete, Assignment):
            self.assessments[assessment][student].remove(assignment_to_delete)
        elif isinstance(assignment_to_delete, str):
            for assignment in self.assessments[assessment][student]:
                if assignment.name == assignment_to_delete:
                    self.assessments[assessment][student].remove(assignment)

    def to_dict(self) -> dict:
        data = {"students": [], "assessments": {}, "grading": self.grading}
        for student in self.students:
            data["students"].append(student.id)
        for assessment in self.assessments:
            data["assessments"][assessment] = {}
            for student in self.assessments[assessment]:
                data["assessments"][assessment][student.id] = []
                for assignment in self.assessments[assessment][student]:
                    data["assessments"][assessment][student.id].append(
                        assignment.to_dict()
                    )
        return data
