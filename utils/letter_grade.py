from utils import globals

def get_letter_grade(percentage: float) -> str:
    for min_percentage, letter_grade in globals.grade_ranges:
        if percentage >= min_percentage:
            return letter_grade
    return "F"