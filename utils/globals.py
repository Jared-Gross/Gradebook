import os

import ujson as json


def initialize():
    global database_location, student_report_html_template, bootstrap_select_css, bootstrap_css, icon_css, main_css, materialize_css, inter_css, bootstrap_select_js, bootstrap_js, jquery_js, main_js, materialize_js, grade_ranges
    database_location = (
        r"C:\Users\Jared\Documents\Code\Python-Projects\Gradiance\database"
    )
    student_report_html_template = (
        os.getcwd() + r"\static\templates\student_report.html"
    )
    bootstrap_select_css = os.getcwd() + r"\static\css\bootstrap-select.css"
    bootstrap_css = os.getcwd() + r"\static\css\bootstrap.css"
    icon_css = os.getcwd() + r"\static\css\icon.css"
    main_css = os.getcwd() + r"\static\css\main.css"
    materialize_css = os.getcwd() + r"\static\css\materialize.min.css"
    inter_css = os.getcwd() + r"\static\Inter\web\inter.css"

    bootstrap_select_js = os.getcwd() + r"\static\js\bootstrap-select.js"
    bootstrap_js = os.getcwd() + r"\static\js\bootstrap.js"
    jquery_js = os.getcwd() + r"\static\js\jquery.js"
    main_js = os.getcwd() + r"\static\js\main.js"
    materialize_js = os.getcwd() + r"\static\js\materialize.min.js"

    grade_ranges = []
    with open("grade_ranges.json", "r") as file:
        grades: dict[str, int] = json.load(file)
        for letter_grade, grade in grades.items():
            grade_ranges.append((grade, letter_grade))
