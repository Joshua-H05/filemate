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


def compute_average(grades_info):
    # requires a dict with grades as keys and weights as values
    weighted_sum = 0
    for grade, weight in grades_info.items():
        weighted_sum += grade * weight

    average = round(weighted_sum / sum(grades_info.values()), 3)
    return average


def compute_gpa():
    pass
