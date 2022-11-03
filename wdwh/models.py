from wdwh import db, login_manager
from flask_login import UserMixin
# from wdwh.db_functions import load_data

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#     data = load_data()
#     if int(userid) <= len(data):
#         user_data = list(data.values())[int(userid)-1]
#         user_username = list(data.keys())[int(userid)-1]
#         user_password = user_data["password"]
#         user_pantry = user_data["pantry"]
#         user_recipes = user_data["recipes"]
#         user = User(userid, user_username, user_password, user_pantry, user_recipes)
#         return user


# def load_user_from_username(username):
#     data = load_data()
#     if username in data.keys():
#         user_data = data[username]
#         user_id = user_data["id"]
#         user_password = user_data["password"]
#         user_pantry = user_data["pantry"]
#         user_recipes = user_data["recipes"]
#         user = User(user_id, username, user_password, user_pantry, user_recipes)
#         return user


# class User():
#     def __init__(self, id, username, password, pantry, recipes):
#         self.id = id
#         self.username = username
#         self.password = password
#         self.pantry = pantry
#         self.recipes = recipes
    
#     def __repr__(self):
#         return f"User {self.username}"
    
#     def is_authenticated(self):
#         data = load_data()
#         if self.username in data.keys():
#             return True
#         return False
    
#     def is_active(self):
#         return self.is_authenticated()
    
#     def is_anonymous(self):
#         return not self.is_authenticated()
    
#     def get_id(self):
#         data = load_data()
#         return str(data[self.username]["id"])
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    ingredients = db.relationship('Ingredient', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exp_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Ingredient('{self.name}', '{self.exp_date}')"