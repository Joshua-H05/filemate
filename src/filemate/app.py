from flask import Flask, redirect, render_template, request
import flask
import flask_login
import random
import pysnooper
from dotenv import load_dotenv
# Python standard libraries
import json
import os
import sqlite3

# Third-party libraries
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from user import User

from filemate import grades_db as gdb

app = Flask(__name__)
load_dotenv()
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(google_id=user_id)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        google_id = userinfo_response.json()["sub"]
        print(type(google_id))
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=google_id, name=users_name, email=users_email
    )

    # Doesn't exist? Add it to the database.
    print(google_id)
    if not User.get(google_id=google_id):
        print("created")
        User.create(google_id=google_id, name=users_name, email=users_email)

    # Begin user session by logging the user in
    login_user(user)
    print("logged in")

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("dashboard.html", user=current_user.name, email=current_user.email)
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/study")
def study():
    return render_template("study.html")


@app.route("/todo")
def to_do():
    return render_template("to_do.html")


@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@app.route("/grades")
def grades_overview():
    user_id = current_user.id
    semesters = gdb.select_student_semesters(user_id=user_id)
    semester_ids = list(semesters.keys())
    semester_ids.sort(reverse=True)
    latest_semester_id = semester_ids[0]
    latest_semester = semesters[latest_semester_id]
    stats = gdb.compute_all_stats(user_id=user_id, semester_id=latest_semester_id)
    averages = stats["averages"]  # dict with subjects as keys and averages as values
    grades = stats["grades"]  # dict with subjects as keys and grades as values
    gpa = stats["gpa"]
    subject_record = gdb.select_all_student_semester_subject_grades(user_id=user_id, semester=latest_semester_id)
    # Returns a dict of dicts, where the keys of the main dict are the student's subjects and the values
    # are dicts containing info on each exam in the subject
    return render_template("sidebar.html", gpa=gpa, averages=averages, grades=grades, subject_record=subject_record,
                           semesters=semesters, current_semester=latest_semester)


if __name__ == "__main__":
    app.run(
        host='127.0.0.1', port="5000", debug=True,
        ssl_context=('cert.pem', 'key.pem'),
    )
