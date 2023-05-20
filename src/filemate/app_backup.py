from flask import Flask, redirect, render_template, request
import flask
import flask_login
import random

from filemate import grades_db as gdb

app = Flask(__name__)
app.secret_key = 'filemate login'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

users = {'foo@bar.tld': {'password': 'secret'}}


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template("login.html")

    email = flask.request.form['email']
    if email in users and flask.request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))

    return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/study")
def study():
    return render_template("study.html")


@app.route("/todo")
def to_do():
    return render_template("to_do.html")


@app.route("/calendar")
def calendar():
    return render_template("calendar.html")


@app.route("/sidebar")
def grades_overview():
    user_id = 1
    semesters = gdb.select_student_semesters(user_id=user_id)
    semester_id = sorted(semesters, key=lambda x: -x[0])[0][0]
    print(user_id)
    print(semester_id)
    stats = gdb.compute_all_stats(user_id=user_id, semester_id=semester_id)
    averages = stats["averages"]  # dict with subjects as keys and averages as values
    grades = stats["grades"]  # dict with subjects as keys and grades as values
    gpa = stats["gpa"]
    subject_record = gdb.select_all_student_semester_subject_grades(user_id=user_id, semester=semester_id)
    # Returns a dict of dicts, where the keys of the main dict are the student's subjects and the values
    # are dicts containing info on each exam in the subject
    return render_template("sidebar.html", gpa=gpa, averages=averages, grades=grades, subject_record=subject_record)