from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, user_data):
        self.id = username
        self.nama = user_data["nama"]
        self.role = user_data["role"]
        self.last_update = user_data["last_update"]
        self.user_data = user_data

    def get_id(self):
        return self.id
