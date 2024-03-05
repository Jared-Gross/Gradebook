import contextlib
import random
import uuid
from datetime import datetime
from typing import Union

from PyQt6.QtGui import QColor

from utils.icons import Icons


class Student:
    def __init__(
        self,
        first_name: str = "",
        middle_name: str = "",
        last_name: str = "",
        gender: str = "",
        birthday: str = "",
        colony: str = "",
        color: tuple[int, int, int] = (0, 0, 0),
        notes: str = "",
    ) -> None:
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.gender = gender
        self.birthday = birthday
        self.colony = colony
        self.id = str(uuid.uuid1())
        self.notes = notes
        self.name: str = f"{self.first_name} {self.last_name}"
        self.color = QColor(color[0], color[1], color[2])
        if gender == "Male":
            self.icon = random.choice(Icons.male_icons)
        else:
            self.icon = random.choice(Icons.female_icons)

    def get_age(self) -> float:
        birth_date = datetime.strptime(self.birthday, "%Y-%m-%d")
        current_date = datetime.now()
        age = (current_date - birth_date).days
        return round(age / 365, 2)

    def get_grade_level(self, age=None) -> str:
        if age is None:
            age = self.get_age()
        if 4 <= age <= 5:
            return "Pre-Kindergarten"
        elif 5 <= age <= 6:
            return "Kindergarten"
        elif 6 <= age <= 7:
            return "Grade 1"
        elif 7 <= age <= 8:
            return "Grade 2"
        elif 8 <= age <= 9:
            return "Grade 3"
        elif 9 <= age <= 10:
            return "Grade 4"
        elif 10 <= age <= 11:
            return "Grade 5"
        elif 11 <= age <= 12:
            return "Grade 6"
        elif 12 <= age <= 13:
            return "Grade 7"
        elif 13 <= age <= 14:
            return "Grade 8"
        elif 14 <= age <= 15:
            return "Grade 9"
        elif 15 <= age <= 16:
            return "Grade 10"
        elif 16 <= age <= 17:
            return "Grade 11"
        elif 17 <= age <= 18:
            return "Grade 12"
        else:
            return "Unknown"

    def get_school_stage(self, age=None) -> str:
        if age is None:
            age = self.get_age()
        if 4 <= age <= 5:
            return "Preschool"
        elif 5 <= age <= 12:
            return "Primary School"
        elif 12 <= age <= 18:
            return "High School"
        else:
            return "Unknown"

    def get_next_grade_levels(self) -> list[tuple[str, int, int]]:
        next_grade_levels = []
        age = self.get_age()
        for _ in range(3):
            current_grade = self.get_grade_level(age)
            age += 1  # Move to the next age
            next_grade = self.get_grade_level(age)
            next_starting_age = age
            next_starting_year = datetime.strptime(self.birthday, "%Y-%m-%d").year + age
            next_grade_levels.append(
                (next_grade, next_starting_age, next_starting_year)
            )

        return next_grade_levels

    def from_dict(self, data: dict):
        self.first_name: str = data["first_name"]
        self.middle_name: str = data["middle_name"]
        self.last_name: str = data["last_name"]
        self.gender: str = data["gender"]
        self.birthday: str = data["birthday"]
        self.colony: str = data["colony"]
        self.notes: str = data.get("notes", "")
        self.id: str = data["id"]
        self.name: str = f"{self.first_name} {self.last_name}"
        self.icon: str = data["icon"]
        self.color = QColor(data["color"][0], data["color"][1], data["color"][2])

    def to_dict(self) -> dict[str, Union[str, int, list[int, int, int]]]:
        return {
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "birthday": self.birthday,
            "colony": self.colony,
            "notes": self.notes,
            "id": self.id,
            "icon": self.icon,
            "color": [self.color.red(), self.color.green(), self.color.blue()],
        }
