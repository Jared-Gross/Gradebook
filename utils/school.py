import ujson as json
import os

from utils import globals
from utils.assignment_template import AssignmentTemplate
from utils.assignment import Assignment
from utils.course import Course
from utils.student import Student


class School:
    def __init__(self, name: str) -> None:
        self.name: str = name
        if not os.path.exists(f"{globals.database_location}/{self.name}"):
            os.makedirs(f"{globals.database_location}/{self.name}")
        self.students: list[Student] = []
        self.courses: list[Course] = []
        self.data = {"students": self.students, "courses": self.courses}

    def add_student(self, student: Student):
        self.students.append(student)

    def remove_student(self, student: Student):
        self.students.remove(student)

    def add_course(self, course: Course):
        self.courses.append(course)

    def remove_course(self, course: Course):
        self.courses.remove(course)

    def to_dict(self) -> dict:
        data = {"students": [], "courses": {}}
        for student in self.students:
            data["students"].append(student.to_dict())
        for course in self.courses:
            data["courses"][course.name] = course.to_dict()
        return data

    def save(self):
        with open(
            f"{globals.database_location}/{self.name}/{self.name}.json", "w"
        ) as file:
            json.dump(self.to_dict(), file, indent=4)

    def get_student(self, id: str) -> Student:
        for student in self.students:
            if student.id == id:
                return student
        return None

    def get_student_from_name(self, name: str) -> Student:
        for student in self.students:
            if f"{student.first_name} {student.last_name}" == name:
                return student
        return None

    def get_course(self, name: str) -> Course:
        for course in self.courses:
            if course.name == name:
                return course
        return None

    def get_enrolled_courses(self, student: Student) -> list[Course]:
        return [
            course for course in self.courses if course.is_student_enrolled(student)
        ]

    def load(self) -> dict:
        data = {}
        self.students.clear()
        self.courses.clear()
        try:
            with open(
                f"{globals.database_location}/{self.name}/{self.name}.json", "r"
            ) as file:
                data = json.load(file)
        except FileNotFoundError:
            self.save()
            return
        for student in data["students"]:
            _student = Student()
            _student.from_dict(data=student)
            self.students.append(_student)
        for course, course_data in data["courses"].items():
            course = Course(course)
            course.grading = course_data["grading"]
            for assessment, assessment_data in course_data["assessments"].items():
                course.add_assessment(assessment)
            for student_id in course_data["students"]:
                course.add_student(self.get_student(student_id))
            for assessment, assessment_data in course_data["assessments"].items():
                for student_id in assessment_data:
                    for assignment_data in assessment_data[student_id]:
                        template = AssignmentTemplate(
                            assignment_data["name"], assignment_data["worth"]
                        )
                        if course.does_template_exist(assessment, template):
                            template = course.get_template(
                                assessment, assignment_data["name"]
                            )
                        else:
                            course.add_template(assessment, template)
                        assignment = Assignment(template)
                        assignment.from_dict(assignment_data)
                        course.add_coursework(
                            assessment,
                            self.get_student(student_id),
                            assignment,
                        )
            # course.load_coursework()
            self.courses.append(course)
