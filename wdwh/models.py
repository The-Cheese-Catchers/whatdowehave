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
    ingredients = db.relationship('PantryIngredient', backref='owner', lazy=True)
    recipes = db.relationship('Recipe', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

    # Pantry Functions
    def getIngredientFromPantry(self, ingr_name):
        return PantryIngredient.query.filter_by(name=ingr_name,user_id=self.id).first()

    def addToPantry(self, ingr_name, qty, date):
        present_ingr = self.getIngredientFromPantry(ingr_name)
        if present_ingr:
            present_ingr.increase(qty)
            present_ingr.setExpDate(date)
        else:
            ingr = PantryIngredient(name=ingr_name,qty=qty,user_id=self.id,exp_date=date)
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

    def makeRecipe(self, recipe_name):
        recipe = Recipe.query.filter_by(name=recipe_name,user_id=self.id).first()
        if not recipe.canMake(self.id):
            return False
        ingrs = Ingredient.query.filter_by(recipe_id=recipe.id)
        for ingredient in ingrs:
            if ingredient.qty == recipe.getIngredient(ingredient.name).qty:
                self.deleteFromPantry(ingredient.name)
            else:
                self.removeFromPantry(ingredient.name, ingredient.qty)
        db.session.commit()
        return True

    def addIngredientsToRecipe(self, recipe, ingredients):
        # ingredients is still in the form (name1, qty1; name2, qty2, ...)
        ingr_qty = ingredients.split(';')
        for each_ingr in ingr_qty:
            i_q = each_ingr.split(',')
            if len(i_q) != 2:
                # Improper entry, abort this recipe
                return False
            ingr_name = i_q[0].strip()
            qty = int(i_q[1].strip())

            ingr = RecipeIngredient(name=ingr_name,qty=qty,recipe_id=recipe.id)
            db.session.add(ingr)
        return True

    def removeIngredientsFromRecipe(self, recipe):
        present_ingrs = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        for present_ingr in present_ingrs:
            db.session.delete(present_ingr)
        db.session.commit()

    def addRecipe(self, name, ingredients, instructions):
        recipe = Recipe(name=name, instructions=instructions,user_id=self.id)
        db.session.add(recipe)
        db.session.commit()
        
        if self.addIngredientsToRecipe(recipe, ingredients):
            db.session.commit()
            return True
        return False
    def modifyRecipe(self, recipe, name, ingredients, instructions):
        # Update info
        recipe.name = name
        recipe.instructions = instructions

        # Update ingredients
        self.removeIngredientsFromRecipe(recipe)
        
        # Add new ingredients
        if self.addIngredientsToRecipe(recipe, ingredients):
            db.session.commit()
            return True
        return False

    def deleteRecipe(self, recipe):
        self.removeIngredientsFromRecipe(recipe)
        db.session.delete(recipe)
        db.session.commit()


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    instructions = db.Column(db.Text)
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True)
    image = db.Column(db.LargeBinary,nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Recipe('{self.name}','{self.instructions}','{self.ingredients}')"

    def getIngredient(self, ingredient):
        return RecipeIngredient.query.filter_by(name=ingredient,recipe_id=self.id).first()
    def modifyRecipe(self, ingredient, qty):
        ingr = self.getIngredient(ingredient)
        if ingr:
            if qty < 0:
                ingr.decrease(qty)
            else:
                ingr.increase(qty)
        else:
            new_ingr = RecipeIngredient(name=ingredient, qty=qty, recipe_id=self.id)
            db.session.add(new_ingr)
        db.session.commit()

    def canMake(self, user_id):
        ingrs = Ingredient.query.filter_by(user_id=user_id)
        for ingredient in ingrs:
            if self.getIngredient(ingredient.name) is None\
                    or self.getIngredient(ingredient.name).qty > ingredient.qty:
                return False

        return True

    def update_instr(self,text):
        self.instructions = text
        db.session.commit()

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Ingredient('{self.name}', '{self.qty}')"

# Extends Ingredient
class PantryIngredient(Ingredient):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exp_date = db.Column(db.DateTime)
    def increase(self, qty):
        self.qty += qty
        db.session.commit()

    def decrease(self, qty):
        self.qty -= qty
        db.session.commit()
    def setExpDate(self, date):
        self.exp_date = date    

# Extends Ingredient
class RecipeIngredient(Ingredient):
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))