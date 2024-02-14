import os
import copy

from utils import globals
from utils.assignment import Assignment
from utils.assignment_template import AssignmentTemplate
from utils.student import Student


class Course:
    def __init__(self, name: str):
        self.name: str = name
        self.grading: dict[str, float] = {}
        self.students: list[Student] = []
        self.assignment_templates: dict[str, list[AssignmentTemplate]] = {}
        self.assessments: dict[str, dict[Student, list[Assignment]]] = {}
        # newpath = f"{globals.database_location}/{self.name}"
        # if not os.path.exists(newpath):
        #     os.makedirs(newpath)

    def add_student(self, student: Student):
        self.students.append(student)
        for assessment in self.assessments:
            self.assessments[assessment][student] = []
            # newpath = f"{globals.database_location}/{self.name}/{student.first_name} {student.last_name}/{assessment}"
            # if not os.path.exists(newpath):
            #     os.makedirs(newpath)

    def remove_student(self, student: Student):
        self.students.remove(student)
        for assessment in self.assessments:
            del self.assessments[assessment][student]

    def is_student_enrolled(self, other_student: Student) -> bool:
        for student in self.students:
            if student == other_student:
                return True
        return False

    def add_assessment(self, name: str):
        self.assessments.setdefault(name, {})
        self.assignment_templates.setdefault(name, [])
        self.grading.setdefault(name, 0.0)
        for student in self.students:
            self.assessments[name].setdefault(student, [])
        # newpath = f"{globals.database_location}/{self.name}/Assessments/{name}"
        # if not os.path.exists(newpath):
        #     os.makedirs(newpath)

    def rename_assessment(self, old_name: str, new_name: str):
        self.assessments[new_name] = self.assessments[old_name]
        del self.assessments[old_name]
        
        self.assignment_templates[new_name] = self.assignment_templates[old_name]
        del self.assignment_templates[old_name]

    def remove_assessment(self, name: str):
        del self.assignment_templates[name]
        del self.assessments[name]
        del self.grading[name]

    def add_template(self, assessment: str, new_template: AssignmentTemplate):
        for template in self.assignment_templates[assessment]:
            if template.name == new_template.name:
                continue
            self.assignment_templates[assessment].append(new_template)
            break
        else:
            self.assignment_templates[assessment].append(new_template)

    def does_template_exist(self, assessment: str, other_template: AssignmentTemplate) -> bool:
        for template in self.assignment_templates[assessment]:
            if template.name == other_template.name:
                return True
        return False

    def get_template(self, assessment: str, template_name: str) -> AssignmentTemplate | None:
        for template in self.assignment_templates[assessment]:
            if template.name == template_name:
                return template
        return None
    
    def sync_assignments(self, student: Student):
        for assessment, templates in self.assignment_templates.items():
            assignments = copy.copy(self.assessments[assessment][student])
            new_assignemts: list[Assignment] = []
            def get_score(other_assignment: Assignment) -> float:
                for assignment in assignments:
                    if assignment.template.name == other_assignment.template.name:
                        return assignment.score
                return 0.0
            
            for template in templates:
                assignment = Assignment(template)
                assignment.score = get_score(assignment)
                new_assignemts.append(assignment)
            self.assessments[assessment][student] = new_assignemts
                # self.add_coursework(assessment, student, assignment)
    
    def add_coursework(self, assessment: str, student: Student, assignment: Assignment):
        self.assessments[assessment][student].append(assignment)
        # template = AssignmentTemplate(assignment.name, assignment.worth)
        # self.assignment_templates[assessment].append(template)

    def remove_coursework(
        self, assessment: str, student: Student, assignment_to_delete: Assignment | str
    ):
        if isinstance(assignment_to_delete, Assignment):
            self.assessments[assessment][student].remove(assignment_to_delete)
            self.assignment_templates[assessment].remove(assignment_to_delete.template)
        elif isinstance(assignment_to_delete, str):
            for assignment in self.assessments[assessment][student]:
                if assignment.template.name == assignment_to_delete:
                    self.assessments[assessment][student].remove(assignment)
                    self.assignment_templates[assessment].remove(assignment.template)
                    
    
    def load_coursework(self):
        for assessment, templates in self.assignment_templates.items():
            for template in templates:
                for student, assignments in self.assessments[assessment].items():
                    for assignment in assignments:
                        assignment.template = template

    def to_dict(self) -> dict:
        data = {"students": [], "assignment_templates": {}, "assessments": {}, "grading": self.grading}
        for student in self.students:
            data["students"].append(student.id)
        # for assessment, templates_data in self.assignment_templates.items():
        #     data['assignment_templates'][assessment] = []
        #     for assignment in templates_data:
        #         data["assignment_templates"][assessment].append(assignment.to_dict())
        for assessment in self.assessments:
            data["assessments"][assessment] = {}
            for student in self.assessments[assessment]:
                data["assessments"][assessment][student.id] = []
                for assignment in self.assessments[assessment][student]:
                    data["assessments"][assessment][student.id].append(
                        assignment.to_dict()
                    )
        return data
