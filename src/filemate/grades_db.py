from peewee import *
from datetime import date


db = SqliteDatabase('grades.db')


class Student(Model):
    user_id = AutoField()
    username = CharField()
    school_section = TextField()

    class Meta:
        database = db


class Semester(Model):
    semester_id = AutoField()
    student = ForeignKeyField(Student, backref="semester")
    name = TextField()

    class Meta:
        database = db


class Grade(Model):
    semester = ForeignKeyField(Semester, backref="semester")
    student = ForeignKeyField(Student, backref="semester")
    grade = FloatField()
    weight = FloatField()
    date = DateField()

    class Meta:
        database = db


def insert_student(username, school_section):
    user = Student.create(username=username, school_section=school_section)
    user.save()


def insert_semester(username, name):
    student = Student.select().where(Student.username == username)
    semester = Semester.create(student=student, name=name)
    semester.save()


def insert_grade(username, semester_name, grade, weight, date):
    semester = Semester.select().where((Semester.student == username) | (Semester.name == semester_name))
    student = Student.select().where(Student.username == username)
    grade = Grade.create(student=student, semester=semester, grade=grade, weight=weight, date=date)
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
    insert_grade(username="bob", semester_name="spring 2023", grade=5.3, weight=1, date=date(2023, 5, 23))


def select_student(id):
    student = Student.select().where(Student.user_id == id)
    print(student)


def select_student_semesters(user_id):
    return Semester.select().where(Semester.student == user_id)


if __name__ == "__main__":
    db.connect()
    db.create_tables([Student, Semester, Grade])
    bob = select_student(1)
    select_student(1)
    print(select_student_semesters(1))

    for student in Student.select():
        print(student.username)

    for semester in Semester.select():
        print(semester.student.username, semester.name)

    for grade in Grade.select():
        print(grade.student.username, grade.semester.name, grade.grade, grade.weight, grade.date)
    db.close()
