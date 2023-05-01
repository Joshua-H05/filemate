from peewee import *

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

    class Meta:
        database = db


db.connect()
db.create_tables([Student, Semester, Grade])
joshua = Student.create(username="Joshua", school_section="SG")
joshua.save()
for student in Student.select():
    print(student.username)
db.close()

