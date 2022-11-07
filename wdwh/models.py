from wdwh import db, login_manager
from flask_login import UserMixin
# from wdwh.db_functions import load_data

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    ingredients = db.relationship('Ingredient', backref='owner', lazy=True)
    recipes = db.relationship('Recipe', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

    # Pantry Functions
    def getIngredientFromPantry(self, ingr_name):
        return Ingredient.query.filter_by(name=ingr_name,user_id=self.id).first()

    def addToPantry(self, ingr_name, qty):
        present_ingr = self.getIngredientFromPantry(ingr_name)
        if present_ingr:
            present_ingr.increase(qty)
        else:
            ingr = Ingredient(name=ingr_name,qty=qty,user_id=self.id)
            db.session.add(ingr)
        db.session.commit()
        return True

    def getIngredientAmount(self, ingr_name):
        present_ingr = self.getIngredientFromPantry(ingr_name)
        return present_ingr.qty

    def removeFromPantry(self, ingr_name, qty):
        present_ingr = self.getIngredientFromPantry(ingr_name)
        present_ingr.decrease(qty)
        return True
    def deleteFromPantry(self, ingr_name):
        present_ingr = self.getIngredientFromPantry(ingr_name)
        if present_ingr:
            db.session.delete(present_ingr)
            db.session.commit()
        return True

    # Recipe Functions
    # def addRecipe(self, name, )

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    instructions = db.Column(db.Text)
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    exp_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

    def __repr__(self):
        return f"Ingredient('{self.name}', '{self.qty}')"

    def increase(self, qty):
        self.qty += qty
        db.session.commit()

    def decrease(self, qty):
        self.qty -= qty
        db.session.commit()