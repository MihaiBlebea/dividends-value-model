import os
from deta import Deta
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id: str, name: str, email: str, profile_pic: str):
        self.id = id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(id: str):
        users_table = Deta(os.getenv("DETA_PROJECT_KEY")).Base("users")
        item = users_table.get(id)
        if item is None:
            return None

        return User(id, item["name"], item["email"], item["profile_pic"])

    @staticmethod
    def create(id: str, name: str, email: str, profile_pic: str):
        users_table = Deta(os.getenv("DETA_PROJECT_KEY")).Base("users")
        users_table.put(
            data={
                "name": name,
                "email": email,
                "profile_pic": profile_pic,
            },
            key=id,
        )
