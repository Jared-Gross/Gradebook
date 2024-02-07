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

        # Define grade ranges and their corresponding letter grades
        grade_ranges = [
            (90, "A+"),
            (85, "A"),
            (80, "A-"),
            (77, "B+"),
            (73, "B"),
            (70, "B-"),
            (69, "C+"),
            (63, "C"),
            (60, "C-"),
            (50, "D"),
            (0, "F"),
        ]
        for min_percentage, letter_grade in grade_ranges:
            if percentage >= min_percentage:
                return letter_grade

        return "F"
