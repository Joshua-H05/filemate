from peewee import *
from datetime import date
import os
import json
from filemate import grades as fg
import pysnooper


PROJECT_ROOT = os.path.abspath(os.curdir)
print(PROJECT_ROOT)
DATA = "data"
db = SqliteDatabase(f"{PROJECT_ROOT}/{DATA}/grades_test.db")
print(f"{PROJECT_ROOT}/{DATA}/grades_test.db")


class User(Model):
    google_id = CharField()
    username = CharField()
    email = CharField()
    password = CharField(null=True)
    school_section = TextField(null=True)
    subjects = TextField()

    class Meta:
        database = db

    def set_subjects(self, subjects):
        self.subjects = json.dumps(subjects)

    def get_subjects(self):
        return json.loads(self.subjects)


class Semester(Model):
    semester_id = AutoField()
    student = ForeignKeyField(User, backref="semester", on_delete="CASCADE")
    name = TextField()

    class Meta:
        database = db


class Grade(Model):
    grade_id = AutoField()
    semester = ForeignKeyField(Semester, backref="semester", on_delete="CASCADE")
    student = ForeignKeyField(User, backref="semester", on_delete="CASCADE")
    subject = TextField()
    grade = FloatField()
    weight = FloatField()
    date = DateField()

    class Meta:
        database = db


# Add
def insert_student(google_id, username, email):
    user = User.create(google_id=google_id, username=username, email=email, subjects=[])
    user.save()


def add_subject(user_id, subject):
    user = User.get(User.user_id == user_id)
    subjects = user.get_subjects()
    subjects.append(subject)
    user.set_subjects(subjects)
    user.save()


def insert_semester(username, name):
    student = User.select().where(User.username == username)
    semester = Semester.create(student=student, name=name)
    semester.save()


def insert_grade(username, semester_id, subject, grade, weight, date):
    student = User.select().where(User.username == username)
    grade = Grade.create(student=student, semester_id=semester_id, subject=subject, grade=grade, weight=weight,
                         date=date)
    grade.save()


# Select
def select_student(email):
    query = User.get(User.email == email)
    results = (query.id, query.username, query.email, query.subjects)
    print(results)
    return results


def select_student_id(id):
    try:
        query = User.get(User.id == id)
        results = (query.id, query.username, query.email, query.subjects)
        print(results)
        return results
    except DoesNotExist:
        return None


def select_google_id(google_id):
    try:
        query = User.get(User.google_id == google_id)
        results = (query.id, query.username, query.email, query.subjects)
        print(results)
        return results
    except DoesNotExist:
        return None


@pysnooper.snoop(depth=2)
def select_student_semesters(user_id):
    print(type(user_id))
    semesters = Semester.select().where(Semester.student == user_id)
    results = {}
    for semester in semesters:
        results[semester.semester_id] = semester.name

    return results


def select_student_semester_grades(user_id, semester):
    grades = Grade.select().where((Grade.student == user_id) & (Grade.semester == semester))
    results = []
    for grade in grades:
        results.append(
            {"subject": grade.subject,
             "grade": grade.grade,
             "weight": grade.weight,
             "date": grade.date})

    return results


def select_student_semester_subject_grades(user_id, semester, subject):
    query = Grade.select().where(
        (Grade.student == user_id) & (Grade.semester == semester) & (Grade.subject == subject))

    results = []
    for grade in query:
        results.append(
            {"grade": grade.grade,
             "weight": grade.weight,
             "date": grade.date})

    return results


def select_all_student_semester_subject_grades(user_id, semester):
    student = User.get((User.id == user_id))
    subjects = student.get_subjects()

    subject_exams = {}

    for subject in subjects:
        subject_exams[subject] = \
            select_student_semester_subject_grades(user_id=user_id, semester=semester, subject=subject)

    return subject_exams


def list_all():
    for student in User.select():
        print(student.username, student.user_id, student.subjects)

    for semester in Semester.select():
        print(semester.student.username, semester.name, semester.semester_id)

    for grade in Grade.select():
        print(grade.student.username, grade.semester.name, grade.subject, grade.grade, grade.weight, grade.date)


# Delete
def delete_student(user_id):
    User.delete().where(User.user_id == user_id).execute()
    Semester.delete().where(Semester.student == user_id).execute()
    Grade.delete().where(Grade.student == user_id).execute()


def delete_semester(semester_id):
    Semester.delete().where(Semester.semester_id == semester_id).execute()
    Grade.delete().where(Grade.semester == semester_id).execute()


def delete_grade(grade_id):
    Grade.delete().where(Grade.grade_id == grade_id).execute()


# compute
def compute_all_semester_averages(id, semester_id):
    averages = {}
    student = User.get(User.id == id)
    subjects = student.get_subjects()
    for subject in subjects:
        exams_and_weights = {}
        query = Grade.select().where(
            (Grade.subject == subject) & (Grade.student == id) & (Grade.semester == semester_id))
        for grade in query:
            exams_and_weights[grade.grade] = grade.weight
        print(exams_and_weights)
        averages[subject] = fg.compute_average(exams_and_weights)

    return averages


def compute_all_semester_grades(averages, section):
    for subject, average in averages.items():
        averages[subject] = fg.compute_grade(average, section=section)
    return averages


def compute_all_stats(user_id, semester_id):
    averages = compute_all_semester_averages(id=user_id, semester_id=semester_id)
    grades = compute_all_semester_grades(averages, section="SG")
    gpa = fg.compute_gpa(grades)
    return {"averages": averages, "grades": grades, "gpa": gpa}


# create

def create_students():
    insert_student(username="bob", school_section="SG")


def create_semesters():
    insert_semester("bob", "spring 2023")
    insert_semester("bob", "fall 2023")


def create_grades():
    insert_grade(username="bob", semester_id=1, subject="Math", grade=5.9, weight=1,
                 date=date(2023, 3, 5))
    insert_grade(username="bob", semester_id=1, subject="Math", grade=5.8, weight=1,
                 date=date(2023, 2, 24))
    insert_grade(username="bob", semester_id=1, subject="Math", grade=5.7, weight=1,
                 date=date(2023, 1, 18))
    insert_grade(username="bob", semester_id=1, subject="Math", grade=5.8, weight=1,
                 date=date(2023, 6, 19))
    insert_grade(username="bob", semester_id=1, subject="Math", grade=5.7, weight=1,
                 date=date(2023, 3, 25))
    insert_grade(username="bob", semester_id=1, subject="Math", grade=5.9, weight=1,
                 date=date(2023, 5, 28))
    insert_grade(username="bob", semester_id=1, subject="English", grade=5.9, weight=1,
                 date=date(2023, 3, 5))
    insert_grade(username="bob", semester_id=1, subject="English", grade=5.66, weight=1,
                 date=date(2023, 1, 5))
    insert_grade(username="bob", semester_id=1, subject="English", grade=5.6, weight=1,
                 date=date(2023, 11, 25))
    insert_grade(username="bob", semester_id=1, subject="English", grade=5.75, weight=1,
                 date=date(2023, 6, 5))
    insert_grade(username="bob", semester_id=1, subject="English", grade=5.8, weight=1,
                 date=date(2023, 9, 5))

    insert_grade(username="bob", semester_id=2, subject="Math", grade=5.9, weight=1,
                 date=date(2023, 3, 5))
    insert_grade(username="bob", semester_id=2, subject="Math", grade=5.8, weight=1,
                 date=date(2023, 2, 24))
    insert_grade(username="bob", semester_id=2, subject="Math", grade=5.7, weight=1,
                 date=date(2023, 1, 18))
    insert_grade(username="bob", semester_id=2, subject="Math", grade=5.8, weight=1,
                 date=date(2023, 6, 19))
    insert_grade(username="bob", semester_id=2, subject="Math", grade=5.7, weight=1,
                 date=date(2023, 3, 25))
    insert_grade(username="bob", semester_id=2, subject="Math", grade=5.9, weight=1,
                 date=date(2023, 5, 28))
    insert_grade(username="bob", semester_id=2, subject="English", grade=5.9, weight=1,
                 date=date(2023, 3, 5))
    insert_grade(username="bob", semester_id=2, subject="English", grade=5.66, weight=1,
                 date=date(2023, 1, 5))


def create_all():
    create_students()
    create_semesters()
    create_grades()


def main():
    db.connect()
    db.create_tables([User, Semester, Grade])
    """
    create_all()
    add_subject(user_id=1, subject="Math")
    add_subject(user_id=1, subject="English")
    list_all()
    stats = compute_all_stats(user_id=1, semester_id=1)
    print(f"Bob\'s averages are: {stats['averages']} \n "
          f"His grades are {stats['grades']}, and his gpa is {stats['gpa']}")
    print(select_student_semester_grades(user_id=1, semester=1))
    print(select_student_semester_subject_grades(user_id=1, semester=1, subject="English1"))
    print(f"Bob's grades are {select_all_student_semester_subject_grades(user_id=1, semester=1)}")"""
    db.close()


if __name__ == "__main__":
    main()
