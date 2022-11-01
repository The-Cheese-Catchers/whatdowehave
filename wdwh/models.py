from wdwh import db, login_manager
from wdwh.db_functions import load_data

@login_manager.user_loader
def load_user(userid):
    data = load_data()
    if int(userid) <= len(data):
        user_data = list(data.values())[int(userid)-1]
        user_username = list(data.keys())[int(userid)-1]
        user_password = user_data["password"]
        user_pantry = user_data["pantry"]
        user = User(userid, user_username, user_password, user_pantry)
        return user


def load_user_from_username(username):
    data = load_data()
    if username in data.keys():
        user_data = data[username]
        user_id = user_data["id"]
        user_password = user_data["password"]
        user_pantry = user_data["pantry"]
        user = User(user_id, username, user_password, user_pantry)
        return user


class User():
    def __init__(self, id, username, password, pantry):
        self.id = id
        self.username = username
        self.password = password
        self.pantry = pantry
    
    def __repr__(self):
        return f"User {self.username}"
    
    def is_authenticated(self):
        data = load_data()
        if self.username in data.keys():
            return True
        return False
    
    def is_active(self):
        return self.is_authenticated()
    
    def is_anonymous(self):
        if self.is_authenticated():
            return False
        return True
    
    def get_id(self):
        data = load_data()
        return str(data[self.username]["id"])