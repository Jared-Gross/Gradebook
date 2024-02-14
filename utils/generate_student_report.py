from utils.assignment import Assignment
from utils.course import Course
from utils.school import School
from utils.student import Student
from utils import globals

from utils.letter_grade import get_letter_grade

class StudentReport:
    def __init__(self, school: School, student: Student):
        self.school = school
        self.student = student
        self.courses = self.school.get_enrolled_courses(self.student)
        with open(globals.student_report_html_template) as file:
            self.student_report_html_template = file.read()
        self.generated_html_file = self.student_report_html_template

    def generate(self) -> str:
        grand_total_score = 0.0
        grand_total_worth = 0.0
        grand_total_weighted_score = 0.0
        grand_total_weighted_worth = 0.0
        self.load_imports()
        self.generated_html_file = self.generated_html_file.replace(
            "[[ STUDENT_NAME ]]", self.student.name
        )

        student_html = ""
        student_html += f"<h1>{self.student.first_name} {self.student.middle_name} {self.student.last_name}</h1>"
        student_html += f"<p>Gender: {self.student.gender}</p>"
        student_html += f"<p>Grade: {self.student.get_grade_level()}</p>"
        student_html += f"<p>School Stage: {self.student.get_school_stage()}</p>"
        student_html += f"<p>Birthday: {self.student.birthday}</p>"
        student_html += f"<p>Age: {self.student.get_age()}</p>"

        summary_html = ""
        summary_html += '<div class="student_summary">'
        summary_html += "<h3>Summary</h3>"
        summary_html += '<table class="responsive-table highlight">'
        summary_html += "<thead><tr>"
        summary_html += "<th>Course</th><th>Points</th><th>Weighted Points</th><th>Percentage</th><th>Letter Grade</th>"
        summary_html += "</tr></thead>"

        page_html = ""

        for course in self.courses:
            course_total_score = 0.0
            course_total_worth = 0.0
            course_total_weighted_score = 0.0
            course_total_weighted_worth = 0.0
            course_html = ""
            course_html += f'<details id="{course.name}" open=true>'
            course_html += f"<summary><h2>{course.name}</h2></summary>"
            course_html += '<div class="course">'
            course_html += '<div class="course_tables">'
            for assessment, assessment_data in course.assessments.items():
                assessment_total_score = 0.0
                assessment_total_worth = 0.0
                if len(course.assessments[assessment][self.student]) == 0:
                    continue
                course_html += '<div class="assessment">'
                course_html += f"<h3>{assessment}</h3>"
                table_html = ""
                table_html += '<table class="fixed responsive-table highlight">'
                table_html += '<col width="40px"/><col width="40px"/><col width="40px"/><col width="40px"/>'
                table_header = "<thead><tr>"
                for header in ["Name", "Score", "Percentage", "Letter Grade"]:
                    table_header += f"<th>{header}</th>"
                table_header += "</tr></thead>"
                table_html += table_header
                table_html += "<tbody>"
                table_rows = ""
                for student, assignments in assessment_data.items():
                    if student != self.student or len(assignments) == 0:
                        continue
                    for assignment in assignments:
                        table_rows += "<tr>"
                        row_data = ""
                        for data in [
                            assignment.template.name,
                            f"{assignment.score}/{assignment.template.worth}",
                            f"{round(assignment.get_percentage(), 2)}%",
                            assignment.get_letter_grade(),
                        ]:
                            row_data += f"<td>{data}</td>"
                        assessment_total_score += assignment.score
                        assessment_total_worth += assignment.template.worth
                        table_rows += row_data
                        table_rows += "</tr>"
                if assessment_total_worth != 0:
                    course_total_weighted_score += (
                        course.grading[assessment]
                        * assessment_total_score
                        / assessment_total_worth
                    )
                    course_total_weighted_worth += course.grading[assessment]
                    table_rows += f"<tr><td><b>Total</b></td><td><b>{round(course.grading[assessment] * assessment_total_score / assessment_total_worth, 2)}/{round(course.grading[assessment], 2)}</b></td><td><b>{round(assessment_total_score / assessment_total_worth * 100,2)}%</b></td><td><b>{get_letter_grade(assessment_total_score/assessment_total_worth*100)}</b></td></tr>"
                else:
                    course_total_weighted_worth += course.grading[assessment]
                    table_rows += f"<tr><td><b>Total</b></td><td><b>0.0/{round(course.grading[assessment], 2)}</b></td><td><b>0.0%</b></td><td><b>{get_letter_grade(0.0)}</b></td></tr>"

                table_html += table_rows
                table_html += "</tbody>"
                table_html += "</table>"
                course_html += table_html
                course_html += "</div>"  # assessment
                course_total_score += assessment_total_score
                course_total_worth += assessment_total_worth
            grand_total_weighted_score += course_total_weighted_score
            grand_total_weighted_worth += course_total_weighted_worth
            summary_html += f'<tr><td><a href="#{course.name}">{course.name}</a></td><td>{round(course_total_score, 2)}/{round(course_total_worth, 2)}</td><td>{round(course_total_weighted_score, 2)}/{course_total_weighted_worth}</td><td>{round(course_total_weighted_score, 2)}%</td><td>{get_letter_grade(course_total_weighted_score/course_total_weighted_worth*100)}</td></tr>'
            course_html += '<div class="page-break"></div>'
            course_html += "</div>"
            course_html += "</div>"
            course_html += "</details>"  # course
            page_html += course_html
            grand_total_score += course_total_score
            grand_total_worth += course_total_worth

        summary_html += f"<tr><td><b>Grand total</b></td><td><b>{round(grand_total_score, 2)}/{grand_total_worth}</b></td><td><b>{round(grand_total_weighted_score, 2)}/{grand_total_weighted_worth}</b></td><td><b>{round(grand_total_weighted_score/grand_total_weighted_worth*100,2)}%</b></td><td><b>{get_letter_grade(grand_total_weighted_score/grand_total_weighted_worth*100)}</b></td></tr>"
        summary_html += "</table>"
        summary_html += "</div>"

        student_html += summary_html

        self.generated_html_file = self.generated_html_file.replace(
            "[[ TABLES ]]", page_html
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ STUDENT ]]", student_html
        )
        with open("test.html", "w") as f:
            f.write(self.generated_html_file)

        return self.generated_html_file

    def load_imports(self):
        self.generated_html_file = self.generated_html_file.replace(
            "[[ BOOTSTRAP_SELECT_JS ]]", globals.bootstrap_select_js
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ BOOTSTRAP_JS ]]", globals.bootstrap_js
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ JQUERY_JS ]]", globals.jquery_js
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ MATERIALIZE_JS ]]", globals.materialize_js
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ MAIN_JS ]]", globals.main_js
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ BOOTSTRAP_SELECT_CSS ]]", globals.bootstrap_select_css
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ BOOTSTRAP_CSS ]]", globals.bootstrap_css
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ ICON_CSS ]]", globals.icon_css
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ MATERIALIZE_CSS ]]", globals.materialize_css
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ MAIN_CSS ]]", globals.main_css
        )
        self.generated_html_file = self.generated_html_file.replace(
            "[[ INTER_CSS ]]", globals.inter_css
        )
