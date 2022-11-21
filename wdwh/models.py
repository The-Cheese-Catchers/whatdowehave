from wdwh import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Users have PantryIngredients and Recipes
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

    # Adds PantryIngredient to the User
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

    # Retrieves ingredient amount
    def getIngredientAmount(self, ingr_name):
        present_ingr = self.getIngredientFromPantry(ingr_name)
        return present_ingr.qty

    # Removes a set amount from the ingredient in the pantry
    def removeFromPantry(self, ingr_name, qty):
        present_ingr = self.getIngredientFromPantry(ingr_name)
        present_ingr.decrease(qty)
        return True
    # Delete an Ingredient completely from a User
    def deleteFromPantry(self, ingr_name):
        present_ingr = self.getIngredientFromPantry(ingr_name)
        if present_ingr:
            db.session.delete(present_ingr)
            db.session.commit()
        return True

    # Adds ingredients to a specific recipe
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

    # Removes ingredients from a specific recipe
    def removeIngredientsFromRecipe(self, recipe):
        present_ingrs = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        for present_ingr in present_ingrs:
            db.session.delete(present_ingr)
        db.session.commit()

    # Adds a recipe to a User
    def addRecipe(self, name, ingredients, instructions):
        recipe = Recipe(name=name, instructions=instructions,user_id=self.id)
        db.session.add(recipe)
        db.session.commit()
        
        if self.addIngredientsToRecipe(recipe, ingredients):
            db.session.commit()
            return True
        return False
    
    # Modifies a User's Recipe
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

    # Deletes a User's Recipe
    def deleteRecipe(self, recipe):
        self.removeIngredientsFromRecipe(recipe)
        db.session.delete(recipe)
        db.session.commit()

    # Says how many times a recipe can be made
    def canMakeRecipe(self, recipe):
        recipe_ingrs = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        maxMakes = 1e9
        for recipe_ingr in recipe_ingrs:
            pantry_ingr = self.getIngredientFromPantry(recipe_ingr.name)
            if not pantry_ingr:
                return 0
            if pantry_ingr.qty < recipe_ingr.qty:
                return 0
            else:
                maxMakes = min(maxMakes, pantry_ingr.qty//recipe_ingr.qty)
        return maxMakes
    
    # Makes recipe using pantry
    def makeRecipe(self, recipe):
        recipe_ingrs = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        for recipe_ingr in recipe_ingrs:
            pantry_ingr = self.getIngredientFromPantry(recipe_ingr.name)
            pantry_ingr.decrease(recipe_ingr.qty)
    
    # Sees which ingredients are missing to make a recipe
    def missingIngredients(self, recipe):
        missing_ingrs = []
        recipe_ingrs = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        for recipe_ingr in recipe_ingrs:
            pantry_ingr = self.getIngredientFromPantry(recipe_ingr.name)
            if not pantry_ingr:
                missing_ingrs.append((recipe_ingr.name, recipe_ingr.qty))
            elif pantry_ingr.qty < recipe_ingr.qty:
                missing_ingrs.append((recipe_ingr.name, recipe_ingr.qty - pantry_ingr.qty))
        return missing_ingrs

# Recipe Class
# - Owned by Users
# - Has RecipeIngredients
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    instructions = db.Column(db.Text)
    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Recipe('{self.name}','{self.instructions}','{self.ingredients}')"

    # Retrieves an Ingredient from the recipe
    def getIngredient(self, ingredient):
        return RecipeIngredient.query.filter_by(name=ingredient,recipe_id=self.id).first()
    # Modifies Recipe
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

    # Checks whether a Recipe can be made by the User
    def canMake(self):
        return self.owner.canMakeRecipe(self)
    # Makes Recipe for User
    def make(self):
        self.owner.makeRecipe(self)
    # Returns the missing ingredients to make this recipe for the User
    def missingIngredients(self):
        return self.owner.missingIngredients(self)
    # Updates the Recipe instructions
    def update_instr(self,text):
        self.instructions = text
        db.session.commit()

# Abstract Ingredient Object
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Ingredient('{self.name}', '{self.qty}')"

# Extends Ingredient
# - Links Ingredients to Users
# - Has expiration date
class PantryIngredient(Ingredient):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exp_date = db.Column(db.DateTime)

    # Increases the quantity
    def increase(self, qty):
        self.qty += qty
        db.session.commit()
    # Decreases the quantity
    def decrease(self, qty):
        self.qty -= qty
        db.session.commit()
    # Updates the expiration date
    def setExpDate(self, date):
        self.exp_date = date    

# Extends Ingredient
# - Links Ingredients to Recipe
class RecipeIngredient(Ingredient):
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))