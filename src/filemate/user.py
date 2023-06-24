from flask_login import UserMixin

import filemate.grades_db as gdb


class User(UserMixin):
    def __init__(self, id_, name, email, subjects=[]):
        self.id = id_
        self.name = name
        self.email = email
        self.subjects = subjects

    @staticmethod
    def get(google_id):
        user = gdb.select_student_id(id=google_id)
        if not user:
            return None
        print(f"id: {user[0]}, name: {user[1]}, email: {user[2]}")
        user = User(id_=user[0], name=user[1], email=user[2])
        return user

    @staticmethod
    def get_email(email):
        user = gdb.select_student(email=email)
        if not user:
            return None
        print(f"id: {user[0]}, name: {user[1]}, email: {user[2]}")
        user = User(id_=user[0], name=user[1], email=user[2])
        return user

    @staticmethod
    def create(id, name, email):
        print(id)
        print(type(id))
        gdb.insert_student(google_id=id, username=name, email=email)
