import ujson as json

from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.student import Student


class School:
    def __init__(self, name: str) -> None:
        self.name: str = name
        globals.database_location += f"/{self.name}"
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
        with open(f"{globals.database_location}/{self.name}.json", "w") as file:
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

    def load(self) -> dict:
        data = {}
        self.students.clear()
        self.courses.clear()
        with open(f"{globals.database_location}/{self.name}.json", "r") as file:
            data = json.load(file)
        for student in data["students"]:
            _student = Student()
            _student.from_dict(data=student)
            self.students.append(_student)
        for course, course_data in data["courses"].items():
            course = Course(name=course)
            course.grading = course_data["grading"]
            for assessment, assessment_data in course_data["assessments"].items():
                course.add_assessment(name=assessment)
            for student_id in course_data["students"]:
                course.add_student(self.get_student(student_id))
            for assessment, assessment_data in course_data["assessments"].items():
                for student_id in assessment_data:
                    for assignment_data in assessment_data[student_id]:
                        assignment = Assignment()
                        assignment.from_dict(assignment_data)
                        course.add_coursework(
                            assessment=assessment,
                            student=self.get_student(student_id),
                            assignment=assignment,
                        )
            self.courses.append(course)
