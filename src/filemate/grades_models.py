from flask import Flask
from peewee import *
import json

from flask_peewee.db import Database
from flask_peewee.auth import Auth, BaseUser


DATABASE = {
    'name': 'grades_test.db',
    'engine': 'peewee.SqliteDatabase',
}
DEBUG = True
SECRET_KEY = 'ssshhhh'
app = Flask(__name__)
app.config.from_object(__name__)
# instantiate the db wrapper
db = Database(app)
auth = Auth(app, db)


class User(db.Model, BaseUser):
    id = AutoField()
    username = CharField()
    password = CharField(null=True)
    email = TextField()
    subjects = TextField()

    class Meta:
        database = db

    def set_subjects(self, subjects):
        self.subjects = json.dumps(subjects)

    def get_subjects(self):
        return json.loads(self.subjects)


class Semester(db.Model):
    semester_id = AutoField()
    student = ForeignKeyField(User, backref="semester", on_delete="CASCADE")
    name = TextField()

    class Meta:
        database = db


class Grade(db.Model):
    grade_id = AutoField()
    semester = ForeignKeyField(Semester, backref="semester", on_delete="CASCADE")
    student = ForeignKeyField(User, backref="semester", on_delete="CASCADE")
    subject = TextField()
    grade = FloatField()
    weight = FloatField()
    date = DateField()

    class Meta:
        database = db


if __name__ == '__main__':
    app.run()
