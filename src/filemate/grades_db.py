from peewee import *
from datetime import date
import json
from filemate import grades as fg
import pysnooper

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
    semester = Semester.select().where((Semester.student == username) & (Semester.name == semester_name))
    student = Student.select().where(Student.username == username)
    grade = Grade.create(student=student, semester=semester, subject=subject, grade=grade, weight=weight, date=date)
    grade.save()


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
    student = Student.get((Student.user_id == user_id))
    subjects = student.get_subjects()

    subject_exams = {}

    for subject in subjects:
        subject_exams[subject] = \
            select_student_semester_subject_grades(user_id=user_id, semester=semester, subject=subject)

    return subject_exams


def list_all():
    for student in Student.select():
        print(student.username, student.user_id, student.subjects)

    for semester in Semester.select():
        print(semester.student.username, semester.name, semester.semester_id)

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


# compute
def compute_all_semester_averages(user_id, semester_id):
    averages = {}
    student = Student.get(Student.user_id == user_id)
    subjects = student.get_subjects()
    for subject in subjects:
        exams_and_weights = {}
        query = Grade.select().where((Grade.subject == subject) & (Grade.student == user_id) & (Grade.semester == semester_id))
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
    averages = compute_all_semester_averages(user_id=user_id, semester_id=semester_id)
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
    insert_grade(username="bob", semester_name="spring 2023", subject="Math", grade=5.9, weight=1,
                 date=date(2023, 5, 23))
    insert_grade(username="bob", semester_name="spring 2023", subject="Math", grade=5.7, weight=1,
                 date=date(2023, 5, 29))
    insert_grade(username="bob", semester_name="spring 2023", subject="Math", grade=5.6, weight=1,
                 date=date(2023, 6, 18))
    insert_grade(username="bob", semester_name="spring 2023", subject="English", grade=6, weight=1,
                 date=date(2023, 5, 23))
    insert_grade(username="bob", semester_name="spring 2023", subject="English", grade=5.5, weight=1,
                 date=date(2023, 6, 23))
    insert_grade(username="bob", semester_name="fall 2023", subject="English", grade=5.83, weight=1,
                 date=date(2022, 9, 23))


def create_all():
    create_students()
    create_semesters()
    create_grades()


def main():
    db.connect()
    db.create_tables([Student, Semester, Grade])
    """create_all()
    add_subject(user_id=1, subject="Math")
    add_subject(user_id=1, subject="English")
    list_all()"""
    stats = compute_all_stats(user_id=1, semester_id=1)
    print(f"Bob\'s averages are: {stats['averages']} \n "
          f"His grades are {stats['grades']}, and his gpa is {stats['gpa']}")
    print(select_student_semester_grades(user_id=1, semester=1))
    print(select_student_semester_subject_grades(user_id=1, semester=1, subject="English1"))
    print(f"Bob's grades are {select_all_student_semester_subject_grades(user_id=1, semester=1)}")
    db.close()


if __name__ == "__main__":
    main()
