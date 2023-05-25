from __future__ import annotations

from datetime import date
from flask_login import UserMixin
import json
from filemate import grades as fg
import pysnooper

from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Float, Date
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, MetaData
import datetime

engine = create_engine("sqlite:///grades_test.db", echo=True)

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(120))
    subjects: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    semesters: Mapped[List["semesters"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    grades: Mapped[List["grades"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return '<User %r>' % self.username

    def set_subjects(self, subjects):
        self.subjects = json.dumps(subjects)

    def get_subjects(self):
        return json.loads(self.subjects)


class Semester(Base):
    __tablename__ = "semester"

    id: Mapped[int] = mapped_column(primary_key=True)
    student: Mapped[int] = mapped_column(ForeignKey("user.id"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    grades: Mapped[List["grades"]] = relationship(back_populates="semester", cascade="all, delete-orphan")

    class Meta:
        database = db


class Grade(Base):
    __tablename__ = "grade"
    id: Mapped[int] = mapped_column(primary_key=True)
    semester: Mapped[int] = mapped_column(ForeignKey("semester.id"))
    student: Mapped[int] = mapped_column(ForeignKey("user.id"))
    subject: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    grade: Mapped[float] = mapped_column(Float(), unique=False)
    weight: Mapped[float] = mapped_column(Float(), unique=False)
    date: Mapped[float] = mapped_column(Date(), unique=False)


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
    conn = engine.connect()
    metadata = MetaData()


if __name__ == "__main__":
    main()
