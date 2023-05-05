from flask import Flask, redirect, render_template, request
import random

from filemate import grades_db as gdb

app = Flask(__name__)


class UserAuthorization:

    def __init__(self):
        self.is_logged_in = False
        self.user_id = None

    def user_login(self):
        if not self.is_logged_in:
            self.user_id = random.choice([1])
        # Display login page
        else:
            return self.user_id


bob = UserAuthorization()


@app.route("/login")
def login():
    pass


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/grades")
def grades_overview():
    user_id = bob.user_id
    stats = gdb.compute_all_stats(user_id=1, semester_id=1)
    averages = stats["averages"]  # dict with subjects as keys and averages as values
    grades = stats["grades"]  # dict with subjects as keys and grades as values
    gpa = stats["gpa"]
    subject_record = gdb.select_all_student_semester_subject_grades(user_id=1, semester=1)
    # Returns a dict of dicts, where the keys of the main dict are the student's subjects and the values
    # are dicts containing info on each exam in the subject
    return render_template("grades.html", gpa=gpa, averages=averages, grades=grades, subject_record=subject_record)


@app.route("/study")
def study():
    return render_template("study.html")


@app.route("/todo")
def to_do():
    return render_template("to_do.html")


@app.route("/calendar")
def calendar():
    return render_template("calendar.html")
