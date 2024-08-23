import random
from datetime import datetime

import jinja2
import tornado

from utils.custom_print import CustomPrint
from utils.sessions import sessions
from utils import globals

loader = jinja2.FileSystemLoader("templates")
env = jinja2.Environment(loader=loader)


class QuestionsHandler(tornado.web.RequestHandler):
    def post(self, game_name_url):
        current_ip = self.request.remote_ip
        if current_ip not in sessions or not sessions[current_ip]["logged_in"]:
            self.redirect("/login")
            return
        grade_level = globals.school.get_student_from_name(sessions[current_ip]['username']).get_grade_level()
        entered_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        game_name = self.get_argument("game")
        template = env.get_template("questions.html")
        sessions[current_ip]["current_game"] = game_name
        sessions[current_ip]["date"] = entered_date
        CustomPrint.print(
            f"INFO - {sessions[current_ip]['username']} entered {game_name}"
        )

        rendered_template = template.render(
            username=sessions[current_ip]["username"],
            game_name=game_name,
            questions=self.generate_questions(grade_level, game_name),
        )
        self.write(rendered_template)

    def generate_question(self, question: str, question_data: dict[str, dict[str, bool]]) -> str:
        html = ""
        html += f"<h4>{question}</h4>"
        for option, is_correct in question_data.items():
            html += f'<label for="{question}-{option}">{option}</label><br>'
            html += f'<input type="radio" id="{question}-{option}" name="{question}" value="{option}" answer="{is_correct}">'
        return html

    def generate_questions(self, grade_level: str, game_name: str) -> str:
        questions = globals.questions_data[grade_level][game_name]
        html = ""
        for question, question_data in questions.items():
            html += self.generate_question(question, question_data)
        return html
