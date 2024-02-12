from utils.letter_grade import get_letter_grade


class Assignment:
    def __init__(self, name: str = "") -> None:
        self.name: str = name
        self.score: float = 0.0
        self.worth: float = 0.0

    def to_dict(self) -> dict:
        return {"name": self.name, "score": self.score, "worth": self.worth}

    def from_dict(self, data: dict):
        self.name = data["name"]
        self.score = float(data["score"])
        self.worth = float(data["worth"])

    def get_percentage(self) -> float:
        try:
            return self.score / self.worth * 100
        except ZeroDivisionError:
            return 0.0

    def get_letter_grade(self) -> str:
        percentage = self.get_percentage()
        return get_letter_grade(percentage)
