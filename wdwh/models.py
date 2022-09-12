from wdwh import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f"User {self.username}"

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    subtype = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f"{self.family}, {self.subtype} {self.name}"

class Pantry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    ingredients = db.relationship('Ingredient', backref='FoundIn', lazy=True)
    
    def __repr__(self):
        return f"{self.user_id} has {self.quantity} units of {self.ingredient_id}"

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    
    def __repr__(self):
        return f"{self.name}"