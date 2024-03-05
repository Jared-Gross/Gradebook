import os

import ujson as json

__version__ = "v0.0.2"


def initialize():
    global database_location, grade_ranges
    with open("DATABASE_LOCATION.txt") as file:
        database_location = os.path.normpath(file.read().strip())

    grade_ranges = []
    with open("grade_ranges.json", "r") as file:
        grades: dict[str, int] = json.load(file)
        grade_ranges.extend(
            (grade, letter_grade) for letter_grade, grade in grades.items()
        )
