from peewee import *
from datetime import date
import json

db = SqliteDatabase('grades.db')


class Student(Model):
    user_id = AutoField()
    username = CharField()
    school_section = TextField()
    subjects = TextField()

    class Meta:
        database = db

    def set_subjects(self, subjects):
        self.subjects = json.dumps(subjects)

    def get_subjects(self):
        return json.loads(self.subjects)


class Semester(Model):
    semester_id = AutoField()
    student = ForeignKeyField(Student, backref="semester", on_delete="CASCADE")
    name = TextField()

    class Meta:
        database = db


class Grade(Model):
    grade_id = AutoField()
    semester = ForeignKeyField(Semester, backref="semester", on_delete="CASCADE")
    student = ForeignKeyField(Student, backref="semester", on_delete="CASCADE")
    subject = TextField()
    grade = FloatField()
    weight = FloatField()
    date = DateField()

    class Meta:
        database = db

# Should I create a table for student gpas?


# Add
def insert_student(username, school_section):
    user = Student.create(username=username, school_section=school_section, subjects=[])
    user.save()


def add_subject(user_id, subject):
    user = Student.get(Student.user_id == user_id)
    subjects = user.get_subjects()
    subjects.append(subject)
    user.set_subjects(subjects)
    user.save()


def insert_semester(username, name):
    student = Student.select().where(Student.username == username)
    semester = Semester.create(student=student, name=name)
    semester.save()


def insert_grade(username, semester_name, subject, grade, weight, date):
    semester = Semester.select().where((Semester.student == username) | (Semester.name == semester_name))
    student = Student.select().where(Student.username == username)
    grade = Grade.create(student=student, semester=semester, subject=subject, grade=grade, weight=weight, date=date)
    grade.save()


def create_students():
    insert_student(username="bob", school_section="IS")
    insert_student(username="tom", school_section="SG")
    insert_student(username="ginny", school_section="SG")


def create_semesters():
    insert_semester("bob", "spring 2023")
    insert_semester("bob", "fall 2023")
    insert_semester("ginny", "spring 2022")
    insert_semester("tom", "spring 2024")


def create_grades():
    insert_grade(username="bob", semester_name="spring 2023", subject="math", grade=5.3, weight=1,
                 date=date(2023, 5, 23))
    insert_grade(username="ginny", semester_name="spring 2022", subject="English", grade=6, weight=1,
                 date=date(2023, 5, 23))


def create_all():
    create_students()
    create_semesters()
    create_grades()


# Select
def select_student(user_id):
    query = Student.select().where(Student.user_id == user_id)
    results = []
    for student in query:
        results.append((student.user_id, student.username, student.school_section))
    return results


def select_student_semesters(user_id):
    semesters = Semester.select().where(Semester.student == user_id)
    results = []
    for semester in semesters:
        results.append((semester.semester_id, semester.student, semester.name))

    return results


def select_student_semester_grades(user_id, semester):
    grades = Grade.select().where((Grade.student == user_id) | (Grade.semester == semester))
    results = []
    for grade in grades:
        results.append((grade.subject, grade.grade, grade.weight, grade.date))

    return results


def select_student_semester_subject_grades(user_id, semester, subject):
    query = Grade.select().where(
        (Grade.student == user_id) | (Grade.semester == semester) | (Grade.subject == subject))

    results = []
    for grade in query:
        results.append((grade.subject, grade.grade, grade.weight, grade.date))

    return results


def list_all():
    for student in Student.select():
        print(student.username, student.user_id, student.subjects)

    for semester in Semester.select():
        print(semester.student.username, semester.name)

    for grade in Grade.select():
        print(grade.student.username, grade.semester.name, grade.subject, grade.grade, grade.weight, grade.date)


# Delete
def delete_student(user_id):
    Student.delete().where(Student.user_id == user_id).execute()
    Semester.delete().where(Semester.student == user_id).execute()
    Grade.delete().where(Grade.student == user_id).execute()


def delete_semester(semester_id):
    Semester.delete().where(Semester.semester_id == semester_id).execute()
    Grade.delete().where(Grade.semester == semester_id).execute()


def delete_grade(grade_id):
    Grade.delete().where(Grade.grade_id == grade_id).execute()


if __name__ == "__main__":
    db.connect()
    db.create_tables([Student, Semester, Grade])

    """ student = select_student(user_id=1)
    print(student)
    semester = select_student_semesters(user_id=1)
    print(semester)
    grades = select_student_semester_grades(user_id=1, semester=1)
    print(grades)
    math_grades = select_student_semester_subject_grades(user_id=1, semester=1, subject="math")
    print(math_grades)"""

    create_all()
    list_all()
    delete_grade(grade_id=2)
    print("deleted grade 2")
    add_subject(1, "math")
    print("bob now studies math")
    list_all()
    db.close()
