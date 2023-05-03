import filemate.grades as grades
import pytest


def test_add_subject():
    pass


def test_delete_subject():
    pass


def test_add_grade():
    pass


def test_delete_grade():
    pass


def test_compute_average():
    assert grades.compute_average({5: 1, 6: 0.5}) == 5.333


def test_compute_grade():
    assert grades.compute_grade(5.88, "SG") == 6


def test_invalid_grade():
    """Checks whether compute_grade() raises error"""
    with pytest.raises(grades.GradeValueError):
        grades.compute_grade(7.5, "IS")


def test_compute_gpa():
    pass


def test_add_semester():
    pass


def test_delete_semester():
    pass
