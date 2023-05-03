import filemate.grades as grades
import filemate.grades_db as gdb
import pytest

def test_add_subject():
    pass


def test_delete_subject():
    pass


def test_add_grade():
    pass


def test_delete_grade():
    pass


def test_compute_gpa():
    pass


def test_add_semester():
    pass


def test_delete_semester():
    pass


def test_compute_all_grades():
    averages = {"math": 5.9, "french": 5.4, "english": 5.8}
    grades = {"math": 6.0, "french": 5.5, "english": 6.0}
    assert gdb.compute_all_semester_grades(averages=averages, section="SG") == grades

