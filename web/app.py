import asyncio
import os
import sys
from datetime import datetime
from io import StringIO

import coloredlogs
import jinja2
import tornado.ioloop
import tornado.web
import tornado.websocket
from ansi2html import Ansi2HTMLConverter
from games.prime_factorization import PrimeFactorizationHandler
from games.hundreds_chart import HundredsChartHandler
from markupsafe import Markup

from utils import globals
from utils.colors import Colors
from utils.custom_print import CustomPrint
from utils.school import School
from utils.score_messages import random_message
from utils.sessions import sessions

globals.initialize()

loader = jinja2.FileSystemLoader("templates")
env = jinja2.Environment(loader=loader)


connected_clients = set()


def print_clients():
    string = ""

    for client, client_data in sessions.items():
        if client_data["logged_in"]:
            client_formatted = f"{Colors.OKGREEN}{client:<10s} - {client_data['username']:<10s} - currently playing: \"{client_data['current_game']}\" - last activity: {client_data['date']}{Colors.BOLD}"
        else:
            client_formatted = f"{Colors.ERROR}{client:<10s} - {client_data['username']:<10s} - logged out at: {client_data['date']}{Colors.BOLD}"
        string += f"{client_formatted:>10s}\n"
    return string + "\n"


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        current_ip = self.request.remote_ip
        if current_ip in sessions and sessions[current_ip]["logged_in"]:
            self.redirect("/dashboard")
        else:
            self.redirect("/login")

    def on_close(self):
        connected_clients.remove(self)


class LogsHandler(tornado.web.RequestHandler):
    def get(self):
        logs = print_clients() + sys.stdout.getvalue()
        converter = Ansi2HTMLConverter()
        logs = Markup(converter.convert(logs))
        self.write(logs)


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        current_ip = self.request.remote_ip
        if current_ip in sessions and sessions[current_ip]["logged_in"]:
            self.redirect("/dashboard")
            return
        template = env.get_template("login.html")
        rendered_template = template.render()
        self.write(rendered_template)
        connected_clients.add(self)

    def post(self):
        globals.school.load()
        current_ip = self.request.remote_ip
        if current_ip in sessions and sessions[current_ip]["logged_in"]:
            CustomPrint.print(
                f"INFO - {sessions[current_ip]['username']} entered dashboard"
            )
            self.redirect("/dashboard")
            return
        username = self.get_argument("username")
        for student in globals.school.students:
            if (
                username.lower() == student.first_name.lower()
                or username.lower() == student.name.lower()
            ):
                login_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sessions[current_ip] = {
                    "username": student.name,
                    "logged_in": True,
                    "current_game": "nothing",
                    "date": login_date,
                }
                self.redirect("/dashboard")
                CustomPrint.print(
                    f"INFO - {sessions[current_ip]['username']} logged in"
                )
                return
        self.redirect("/login_failed")


class LogoutHandler(tornado.web.RequestHandler):
    def post(self):
        current_ip = self.request.remote_ip
        logout_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sessions[current_ip]["logged_in"] = False
        sessions[current_ip]["date"] = logout_date
        CustomPrint.print(f"INFO - {sessions[current_ip]['username']} logged out")
        self.redirect("/login")


class LoginFailedHandler(tornado.web.RequestHandler):
    def get(self):
        template = env.get_template("login_failed.html")
        rendered_template = template.render()
        self.write(rendered_template)


class DashboardHandler(tornado.web.RequestHandler):
    def get(self):
        current_ip = self.request.remote_ip
        if current_ip not in sessions or not sessions[current_ip]["logged_in"]:
            self.redirect("/login")
            return
        if sessions[current_ip]["current_game"] != "nothing":
            CustomPrint.print(
                f"INFO - {sessions[current_ip]['username']} exited {sessions[current_ip]['current_game']}"
            )
        else:
            CustomPrint.print(
                f"INFO - {sessions[current_ip]['username']} entered dashboard"
            )
        sessions[current_ip]["current_game"] = "nothing"
        template = env.get_template("dashboard.html")
        rendered_template = template.render(
            username=sessions[current_ip]["username"],
            games={"Prime Factorization": "prime_factorization", "Hundreds Chart": "hundreds_chart"},
        )
        self.write(rendered_template)

    def post(self):
        pass

    def on_close(self):
        connected_clients.remove(self)


class ViewScoreHandler(tornado.web.RequestHandler):
    def get(self):
        current_ip = self.request.remote_ip
        if current_ip not in sessions or not sessions[current_ip]["logged_in"]:
            self.redirect("/login")
            return
        sessions[current_ip]["current_game"] = "nothing"
        score = self.get_query_argument("score", default=0)
        worth = self.get_query_argument("worth", default=0)
        checks_used = self.get_query_argument("checks_used", default=0)
        html_name = self.get_query_argument("game_played", default="")
        game_played = html_name.replace("_", " ").title()
        template = env.get_template("score.html")
        rendered_template = template.render(
            username=sessions[current_ip]["username"],
            game_name=game_played,
            game_url=html_name,
            score=score,
            worth=worth,
            checks_used=checks_used,
            message=random_message(float(score)),
        )
        self.write(rendered_template)


class SubmitScoreHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            current_ip = self.request.remote_ip
            if current_ip not in sessions or not sessions[current_ip]["logged_in"]:
                self.redirect("/login")
                return
            score = self.get_body_argument("score", 0)
            worth = self.get_body_argument("worth", 0)
            checks_used = self.get_body_argument("checks_used", 0)
            game_played = self.get_body_argument("game_played", "")
            self.write(
                {
                    "success": True,
                    "redirect": f"/view_score?score={score}&worth={worth}&checks_used={checks_used}&game_played={game_played}",
                }
            )
            CustomPrint.print(
                f"INFO - {sessions[current_ip]['username']} - score: {score}/{worth} - played: {game_played} - checks: {checks_used}"
            )
        except Exception as e:
            self.set_status(500)
            self.write("An error occurred: " + str(e))


def make_app():
    settings = {
        "cookie_secret": "I_AM_RANDOM",
        "login_url": "/login",
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/logs", LogsHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/login_failed", LoginFailedHandler),
            (r"/dashboard", DashboardHandler),
            (r"/submit-score", SubmitScoreHandler),
            (r"/view_score", ViewScoreHandler),
            (r"/prime_factorization", PrimeFactorizationHandler),
            (r"/hundreds_chart", HundredsChartHandler),
        ],
        **settings,
    )


async def main():
    coloredlogs.install(level="INFO")
    sys.stdout = StringIO()
    CustomPrint.print(
        """
                      .@@@@@@@@@@@/
                @@@@@@@@@@@ ((,@@@@@@@@@@,
            @@@@ ((( *@@@&((((( @@@@ ((( @@@@,
         @@@@@@@@ (((( @@ ((((( @@@ (((  @@@@@@@
       @@@@@@@@@@@@&// @@@     @@@@*/&@@@@@@@@@@@@@                   ▄███▄                              ▄█
     @@ (((* @@@@   .@@@@@@@@@@@@@@@%   @@@@& ((( @@.               █▀ ████  ▄                            ██    ▄
    @@@. ((((( @@  ((((( @@#  @@@ ((((( *@@ ((((( @@@@             █  █▀ ████                             ██   ███
  ,@@@@@(  ,(, @@  (((((( @@@@@/ (((((/ &@  (,   @@@@@@           █  ██   ██                              ██    ▀
  @@@@@@@@@@&  %@@   /(   @@@@@@  ((   @@@   @@@@@@@@@@@         █  ███                                   ██
 @@.(((((( @@   @@@@   #@@@   @@@@    @@@   @@@.((((( @@.       ██   ██        ▄██  ▄███     ▄██▄     ▄██ ██  ███       ▄███   ███  ████      ████      ▄██
 @  ((((((  @@#   @@@@#     @@&    @@@@,   @@@ ((((((( *@       ██   ██   ▄█▄   ████ ████ █ █ ███  ▄ █████████ ███     ▄████  █ ████ ████ █  █ ███  ▄  █ ███
%@@@@    #@@@@@@@     @@@   *   @@@/     @@@@@@@    @@@@@       ██   ██  ████  █ ██   ████ █   ████ ██   ████   ██   ▄█   ████   ██   ████  █   ████  █   ███
/@@@@@@@@ ((( @@@@@@/    @     @@    @@@@@@@,((*@@@@@@@@@       ██   ██ █  ████  ██       ██    ██  ██    ██    ██   ██    ██    ██    ██  ██        ██    ███
 @@@@@@@#    @@@ (( @@@           @@@@(((/@@@    @@@@@@@@       ██   ███    ██   ██       ██    ██  ██    ██    ██   ██    ██    ██    ██  ██        ████████
 @@@@@@@@@@@@@@ (( .@@@@#        @@@@@ ,((.@@@@@@@@@@@@@         ██  ██     █    ██       ██    ██  ██    ██    ██   ██    ██    ██    ██  ██        ███████
  @@@@@@@@@@@@@@@@@@@@@@@       @@@@@@@@@@@@@@@@@@@@@@@*          ██ █      █    ██       ██    ██  ██    ██    ██   ██    ██    ██    ██  ██        ██
                       @@@      @@                                 ███     █     ██       ██    ██  ██    ██    ██   ██    ██    ██    ██  ███     █ ████    █
    @@@@@@@@@@@@@@@@@  @@@      @@   @@@@@@@@@@@@@@@@               ███████      ███       █████ ██  █████      ███ █ █████ ██   ███   ███  ███████   ███████▀
                       @@@      @@                                    ███         ███       ███   ██  ███        ███   ███   ██   ███   ███  █████     █████
         @@@@@@@@@@@   @@       @@@  *@@@@@@@@@@@
                     @@@         @@@.
              &&@@@@@@             @@@@@@&&&
"""
    )
    app = make_app()
    app.listen(8888, address="10.11.2.159")
    CustomPrint.print("INFO - Server started")
    shutdown_event = asyncio.Event()
    await shutdown_event.wait()


if __name__ == "__main__":
    asyncio.run(main())
