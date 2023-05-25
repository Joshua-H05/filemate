from flask_login import UserMixin

import filemate.grades_db as gdb


class User(UserMixin):
    def __init__(self, id_, name, email, subjects=[]):
        self.id = id_
        self.name = name
        self.email = email
        self.subjects = subjects

    @staticmethod
    def get(email):
        user = gdb.select_student(email=email)
        if not user:
            return None

        user = User(id_=user[0], name=user[1], email=user[2])
        return user

    @staticmethod
    def create(name, email):
        gdb.insert_student(username=name, email=email)
