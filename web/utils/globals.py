import os

import ujson as json

from utils.school import School

__version__ = "v0.0.2"


def initialize():
    global database_location, grade_ranges, games_config, school, questions_data, default_school
    
    with open("DATABASE_LOCATION.txt") as file:
        database_location = os.path.normpath(file.read().strip())

    with open("DEFAULT_SCHOOL.txt") as file:
        default_school = os.path.normpath(file.read().strip())

    grade_ranges = []
    with open("grade_ranges.json", "r") as file:
        grades: dict[str, int] = json.load(file)
        grade_ranges.extend(
            (grade, letter_grade) for letter_grade, grade in grades.items()
        )
    with open('games/games_config.json') as file:
        games_config = json.load(file)

    with open(f"{database_location}/{default_school}/Questions.json") as file:
        questions_data = json.load(file)

    school = School(default_school)
    school.load()
