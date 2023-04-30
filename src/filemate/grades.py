class GradeValueError(ValueError):
    pass


def compute_grade(average, section):
    if section == "SG":
        limit = 6
    elif section == "IS":
        limit = 7

    if average < 0 or average > limit:
        raise GradeValueError

    else:
        return round(average * 2) / 2

