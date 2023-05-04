from flask import Flask, redirect, render_template, request

from filemate import grades_db as gdb

app = Flask(__name__)


@app.route("/grades")
def grades_overview():
    stats = gdb.compute_all_stats(user_id=1, semester_id=1)
    averages = stats["averages"]  # dict with subjects as keys and averages as values
    grades = stats["grades"]  # dict with subjects as keys and grades as values
    gpa = stats["gpa"]
    subject_record = gdb.select_all_student_semester_subject_grades(user_id=1, semester=1)
    # Returns a dict of dicts, where the keys of the main dict are the student's subjects and the values
    # are dicts containing info on each exam in the subject
    return render_template("grades.html", gpa=gpa, averages=averages, grades=grades, subject_record=subject_record)
