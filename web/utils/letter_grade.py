from utils import globals


def get_letter_grade(percentage: float) -> str:
    return next(
        (
            letter_grade
            for min_percentage, letter_grade in globals.grade_ranges
            if percentage >= min_percentage
        ),
        "F",
    )
