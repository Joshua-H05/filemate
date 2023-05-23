from peewee import *
from flask import Flask
from flask_peewee.db import Database
from flask_peewee.auth import Auth, BaseUser
from datetime import date
import json
from filemate import grades as fg
import pysnooper


db = SqliteDatabase('grades.db')
app = Flask(__name__)


class User(Model, BaseUser):
    id = AutoField()
    username = CharField()
    password = CharField(null=True)
    email = TextField()
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
def insert_student(username, email):
    user = User.create(username=username, email=email, subjects=[])
    user.save()


def add_subject(id, subject):
    user = User.get(User.id == id)
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
def select_student(id):
    query = User.select().where(User.id == id)
    results = []
    for student in query:
        results.append((student.id, student.username, student.school_section))
    return results


def select_student_email(email):
    query = User.select().where(User.email == email)
    results = []
    for student in query:
        results.append((student.id, student.username, student.school_section))
    return results


@pysnooper.snoop()
def select_student_semesters(id):
    semesters = Semester.select().where(Semester.student == id)
    results = {}
    for semester in semesters:
        results[semester.semester_id] = semester.name

    print(results)

    return results


def select_student_semester_grades(id, semester):
    grades = Grade.select().where((Grade.student == id) & (Grade.semester == semester))
    results = []
    for grade in grades:
        results.append(
            {"subject": grade.subject,
             "grade": grade.grade,
             "weight": grade.weight,
             "date": grade.date})

    return results


def select_student_semester_subject_grades(id, semester, subject):
    query = Grade.select().where(
        (Grade.student == id) & (Grade.semester == semester) & (Grade.subject == subject))

    results = []
    for grade in query:
        results.append(
            {"grade": grade.grade,
             "weight": grade.weight,
             "date": grade.date})

    return results


def select_all_student_semester_subject_grades(id, semester):
    student = User.get((User.id == id))
    subjects = student.get_subjects()

    subject_exams = {}

    for subject in subjects:
        subject_exams[subject] = \
            select_student_semester_subject_grades(id=id, semester=semester, subject=subject)

    return subject_exams


def list_all():
    for student in User.select():
        print(student.username, student.id, student.subjects)

    for semester in Semester.select():
        print(semester.student.username, semester.name, semester.semester_id)

    for grade in Grade.select():
        print(grade.student.username, grade.semester.name, grade.subject, grade.grade, grade.weight, grade.date)


# Delete
def delete_student(id):
    User.delete().where(User.id == id).execute()
    Semester.delete().where(Semester.student == id).execute()
    Grade.delete().where(Grade.student == id).execute()


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


def compute_all_stats(id, semester_id):
    averages = compute_all_semester_averages(id=id, semester_id=semester_id)
    grades = compute_all_semester_grades(averages, section="SG")
    gpa = fg.compute_gpa(grades)
    return {"averages": averages, "grades": grades, "gpa": gpa}


# create
def create_students():
    insert_student(username="bob", email="trial@gmail.com")


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


@pysnooper.snoop()
def main():
    db.connect()
    db.create_tables([User, Semester, Grade])
    create_all()
    add_subject(id=1, subject="Math")
    add_subject(id=1, subject="English")
    list_all()
    stats = compute_all_stats(id=1, semester_id=1)
    print(f"Bob\'s averages are: {stats['averages']} \n "
          f"His grades are {stats['grades']}, and his gpa is {stats['gpa']}")
    print(select_student_semester_grades(id=1, semester=1))
    print(select_student_semester_subject_grades(id=1, semester=1, subject="English1"))
    print(f"Bob's grades are {select_all_student_semester_subject_grades(id=1, semester=1)}")

    semesters = select_student_semesters(id=1)
    print(type(semesters))
    db.close()


if __name__ == "__main__":
    main()
