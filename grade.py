"""
grade.py
---------
Grade calculation utilities for SmartGrade System
"""

from config import TOTAL_MARKS


def calculate_total(slide_quality, delivery, qna):
    """
    Calculate total marks.
    """
    return int(slide_quality) + int(delivery) + int(qna)


def calculate_percentage(total):
    """
    Calculate percentage out of TOTAL_MARKS.
    """
    percentage = (float(total) / TOTAL_MARKS) * 100
    return round(percentage, 2)


def calculate_grade(total):
    """
    Return grade based on total marks.
    """

    if total >= 27:
        return "A+"

    elif total >= 24:
        return "A"

    elif total >= 21:
        return "B+"

    elif total >= 18:
        return "B"

    elif total >= 15:
        return "C"

    elif total >= 12:
        return "D"

    else:
        return "F"


def grade_color(grade):
    """
    Return a color for displaying grades.
    """

    colors = {
        "A+": "green",
        "A": "green",
        "B+": "blue",
        "B": "blue",
        "C": "orange",
        "D": "red",
        "F": "darkred"
    }

    return colors.get(grade, "black")