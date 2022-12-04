"""
This file contains the classes:
- User
- Recipe
- Ingredient
- PantryIngredient (extends Ingredient)
- RecipeIngredient (extends Ingredient)

This file acts as the MODEL in the MVC design pattern, since it holds
the class structure and database functions.

The Model contains only the pure application data,
it contains no logic describing how to present the data to a user.
"""
# pylint: disable=consider-using-f-string
from flask_login import UserMixin
from wdwh import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """ Loads the specific user """
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """ Class describing Users who have pantries and recipes """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    ingredients = db.relationship('PantryIngredient', backref='owner', lazy=True)
    recipes = db.relationship('Recipe', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

    def get_ingredient_from_pantry(self, ingr_name):
        """ Gets the ingredient object from the pantry by name """
        return PantryIngredient.query.filter_by(name=ingr_name,user_id=self.id).first()

    def set_pantry_ingredient(self, ingr_name, qty, date, units):
        """ Sets a pantry object for a user """
        present_ingr = self.get_ingredient_from_pantry(ingr_name)
        if present_ingr:
            present_ingr.set_qty(qty)
            present_ingr.set_exp_date(date)
            present_ingr.set_units(units)
        else:
            ingr = PantryIngredient(name=ingr_name,qty=qty,
                    units=units,user_id=self.id,exp_date=date)
            db.session.add(ingr)
        db.session.commit()

    def add_to_pantry(self, ingr_name, qty, date, units):
        """ Adds a pantry ingredient to a user's pantry """
        present_ingr = self.get_ingredient_from_pantry(ingr_name)
        if present_ingr:
            present_ingr.increase(qty)
            present_ingr.set_exp_date(date)
            present_ingr.set_units(units)
        else:
            ingr = PantryIngredient(name=ingr_name,qty=qty,units=units,
                    user_id=self.id,exp_date=date)
            db.session.add(ingr)
        db.session.commit()

    def get_ingredient_amount(self, ingr_name):
        """ Gets the amount of specific ingredient in the pantry """
        present_ingr = self.get_ingredient_from_pantry(ingr_name)
        if not present_ingr:
            return 0
        return present_ingr.qty

    def remove_from_pantry(self, ingr_name, qty, units):
        """ Removes an amount of an ingredient from the pantry """
        present_ingr = self.get_ingredient_from_pantry(ingr_name)
        present_ingr.decrease(qty)
        present_ingr.set_units(units)
        db.session.commit()

    def delete_from_pantry(self, ingr_name):
        """ Deletes an ingredient from a user's pantry """
        present_ingr = self.get_ingredient_from_pantry(ingr_name)
        if present_ingr:
            db.session.delete(present_ingr)
            db.session.commit()

    def __add_ingredients_to_recipe(self, recipe, ingredients):
        """ Adds ingredients to a specific recipe """
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

    def __remove_ingredients_from_recipe(self, recipe):
        """ Removes ingredients from a specific recipe """
        present_ingrs = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        for present_ingr in present_ingrs:
            db.session.delete(present_ingr)
        db.session.commit()

    def add_recipe(self, name, ingredients, instructions):
        """ Adds a recipe to a user """
        recipe = Recipe(name=name, instructions=instructions,user_id=self.id)
        db.session.add(recipe)
        db.session.commit()

        if self.__add_ingredients_to_recipe(recipe, ingredients):
            db.session.commit()
            return True
        return False

    def modify_recipe(self, recipe, name, ingredients, instructions):
        """ Modifies a user's recipe """
        # Update info
        recipe.name = name
        recipe.instructions = instructions

        # Update ingredients
        self.__remove_ingredients_from_recipe(recipe)

        # Add new ingredients
        if self.__add_ingredients_to_recipe(recipe, ingredients):
            db.session.commit()
            return True
        return False

    def delete_recipe(self, recipe):
        """ Deletes a user's recipe """
        self.__remove_ingredients_from_recipe(recipe)
        db.session.delete(recipe)
        db.session.commit()

    def can_make_recipe(self, recipe):
        """ Checks how many times a recipe can be made """
        recipe_ingrs = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        max_makes = 1e9
        for recipe_ingr in recipe_ingrs:
            pantry_ingr = self.get_ingredient_from_pantry(recipe_ingr.name)
            if not pantry_ingr:
                return 0
            if pantry_ingr.qty < recipe_ingr.qty:
                return 0
            max_makes = min(max_makes, pantry_ingr.qty//recipe_ingr.qty)
        return max_makes

    def make_recipe(self, recipe):
        """ Makes a recipe using the user's pantry """
        recipe_ingrs = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        for recipe_ingr in recipe_ingrs:
            pantry_ingr = self.get_ingredient_from_pantry(recipe_ingr.name)
            pantry_ingr.decrease(recipe_ingr.qty)
        db.session.commit()

    def missing_ingredients(self, recipe):
        """ Finds missing ingredients to make a recipe """
        missing_ingrs = []
        recipe_ingrs = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        for recipe_ingr in recipe_ingrs:
            pantry_ingr = self.get_ingredient_from_pantry(recipe_ingr.name)
            if not pantry_ingr:
                missing_ingrs.append((recipe_ingr.name, recipe_ingr.qty))
            elif pantry_ingr.qty < recipe_ingr.qty:
                missing_ingrs.append((recipe_ingr.name, recipe_ingr.qty - pantry_ingr.qty))
        return missing_ingrs

    def search_recipes(self, search_term):
        """ Searches a User's recipes """
        all_recipes = Recipe.query.filter_by(user_id=self.id).all()
        valid_recipes = [r for r in all_recipes if search_term.lower() in r.name.lower()]
        return valid_recipes


class Recipe(db.Model):
    """ Class describing Recipes which have ingredients """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    instructions = db.Column(db.Text)
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True)
    image = db.Column(db.LargeBinary,nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Recipe('{self.name}','{self.instructions}','{self.ingredients}')"

    def get_ingredient(self, ingredient):
        """ Retrieves an ingredient from the recipe """
        return RecipeIngredient.query.filter_by(name=ingredient,recipe_id=self.id).first()

    def can_make(self):
        """ Checks whether a Recipe can be made by the User """
        return self.owner.can_make_recipe(self)

    def make(self):
        """ Makes the recipe for a user """
        self.owner.make_recipe(self)

    def missing_ingredients(self):
        """ Returns the missing ingredients to make this recipe for the user """
        return self.owner.missing_ingredients(self)

    def update_instr(self,text):
        """ Updates the recipe instructions """
        self.instructions = text
        db.session.commit()


class Ingredient(db.Model):
    """ Abstract class which describes Ingredients """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    units = db.Column(db.String(100))

    def __repr__(self):
        return f"Ingredient('{self.name}', '{self.qty}')"

    def set_qty(self, new_qty):
        """ Sets the quantity for an ingredient """
        if new_qty:
            self.qty = new_qty

    def set_units(self, new_units):
        """ Sets the units for an ingredient """
        if new_units:
            self.units = new_units


class PantryIngredient(Ingredient):
    """ Extends Ingredient to have a User and expiration date """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exp_date = db.Column(db.DateTime)

    def increase(self, qty=1):
        """ Increases the quantity for a pantry ingredient """
        self.qty += qty

    def decrease(self, qty=1):
        """ Decreases the quantity for a pantry ingredient """
        self.qty -= qty

    def set_exp_date(self, date):
        """ Updates the expiration date """
        self.exp_date = date
        db.session.commit()


class RecipeIngredient(Ingredient):
    """ Extends Ingredient to have a Recipe """
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
