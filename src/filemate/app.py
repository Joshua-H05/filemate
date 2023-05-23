from flask import Flask, redirect, render_template, request
from dotenv import load_dotenv
# Python standard libraries
import json
import os

# Third-party libraries
from flask import Flask, redirect, request, url_for

from oauthlib.oauth2 import WebApplicationClient
import requests
from flask_peewee.auth import Auth
from flask_peewee.db import Database

# Internal imports

from filemate import grades_db as gdb

DATABASE = {
    'name': 'grades.db',
    'engine': 'peewee.SqliteDatabase',
}
DEBUG = True
SECRET_KEY = 'ssshhhh'
app = Flask(__name__)
app.config.from_object(__name__)
# instantiate the db wrapper
db = Database(app)
auth = Auth(app, db)


load_dotenv()
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db


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
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = gdb.User(username=users_name, email=users_email)

    # Doesn't exist? Add it to the database.
    """query = gdb.select_student_email(email=users_email)
    if not query:
        gdb.insert_student(username=users_name, email=users_email)"""

    # Begin user session by logging the user in
    auth.login_user(user)
    print("logged in")

    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@auth.login_required
def logout():
    auth.logout_user()
    return redirect(url_for("index"))


@app.route("/")
def index():
    if auth.get_logged_in_user():
        return render_template("dashboard.html", user=auth.get_logged_in_user().name,
                               email=auth.get_logged_in_user().email)
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


@app.route("/sidebar")
def grades_overview():
    id = 1
    semesters = gdb.select_student_semesters(id=id)
    print(f"semesters: {semesters}")
    semester_ids = list(semesters.keys())
    semester_ids.sort(reverse=True)
    print(semester_ids)
    latest_semester_id = semester_ids[0]
    latest_semester = semesters[latest_semester_id]
    print(id)
    print(latest_semester_id)
    stats = gdb.compute_all_stats(id=id, semester_id=latest_semester_id)
    averages = stats["averages"]  # dict with subjects as keys and averages as values
    grades = stats["grades"]  # dict with subjects as keys and grades as values
    gpa = stats["gpa"]
    subject_record = gdb.select_all_student_semester_subject_grades(id=id, semester=latest_semester_id)
    # Returns a dict of dicts, where the keys of the main dict are the student's subjects and the values
    # are dicts containing info on each exam in the subject
    return render_template("sidebar.html", gpa=gpa, averages=averages, grades=grades, subject_record=subject_record,
                           semesters=semesters, current_semester=latest_semester)


if __name__ == "__main__":
    app.run(ssl_context="adhoc")
