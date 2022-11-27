import os
import sqlite3
from sqlite3 import Error
from wdwh import app, db, bcrypt
from wdwh.forms import *
from wdwh.models import User, PantryIngredient, RecipeIngredient, Recipe
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename


# Defines the home page
# - Renders the home.html file and displays in browser
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home")


# Defines the registration page
# - Renders the registration.html file and displays in browser
# - Adds username and salted+hashed password to database 
# - Redirects to home page when registration is complete
@app.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    register_form = RegistrationForm()
    if register_form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode()
        user = User(username=register_form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! You are now able to log in!","success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=register_form)


# Defines the login page
# - Renders the login.html file and displays in browser
# - Checks if the username and the entered salted+hashed password are in the database
# - Redirects to homepage when login is complete
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login unsuccessful. Please check username and password.", "danger")
    return render_template("login.html", title="Login", form=login_form)


# Defines the logout page
# - Logs out the user and redirects to the home page
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# Defines the enter recipe page
# - Renders the enter_recipe.html file and displays in browser
# - Allows user to update the recipe
@app.route("/enter_recipe", methods=["GET", "POST"])
@login_required
def enter_recipe():
    recipe_form = EnterRecipeForm()
    if recipe_form.validate_on_submit():
        recipe_name = recipe_form.recipe_name.data
        instructions = recipe_form.instructions.data
        ingredients = recipe_form.ingredients.data
        image = recipe_form.image.data
        filename = secure_filename(image.filename)
        image.save('wdwh/images/'+filename)
        image = image.read()
        if current_user.addRecipe(recipe_name, ingredients, instructions, image):
            flash(f"Recipe created! You should now be able to search for the recipe in the search bar.","success")
            return redirect(url_for("search_recipe"))
        else:
            flash("Ingredients formatted incorrectly, try again","danger")
            recipe = Recipe.query.filter_by(name=recipe_name,user_id=current_user.id).first()
            return redirect(url_for("update_recipe",recipe_id=recipe.id))
    return render_template("enter_recipe.html", title="Create a Recipe", form=recipe_form,
    legend="Enter Recipe Information")


# Defines the search recipe page
# - Renders the search_recipe.html file and displays in browser
# - Allows the user to search for many other recipes by querying an API
@app.route("/search_recipe", methods=["GET", "POST"])
@login_required
def search_recipe():
    search_form = SearchRecipeForm()
    if search_form.validate_on_submit():
        recipe_name = search_form.query.data
        # SEARCH API FOR THIS RECIPE AND LIST OUT DETAILS ON SEPARATE PAGE
    all_recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    return render_template("search_recipe.html", title="Search Recipe", 
                form=search_form, recipes=all_recipes, RecipeIngredient=RecipeIngredient)


# Defines the pantry page
# - Renders the my_pantry.html file and displays in browser
# - Displays each ingredient in a table with buttons to update or delete
@app.route("/my_pantry", methods=["GET", "POST"])
@login_required
def my_pantry():
    add_ingr_form = AddIngredientForm()
    if add_ingr_form.validate_on_submit():
        # Capitalize all ingredients
        ingr_name = add_ingr_form.ingr_name.data.capitalize()
        qty = add_ingr_form.qty.data
        date = add_ingr_form.date.data
        units = add_ingr_form.units.data.capitalize()

        # Adding to the Pantry
        if add_ingr_form.add.data:
            if not qty:
                flash("Can't add without an amount","danger")
            else:
                current_user.addToPantry(ingr_name, qty, date, units)

        # Removing from the Pantry
        if add_ingr_form.remove.data:
            if not qty:
                flash("Can't remove without an amount","danger")
            if not current_user.getIngredientFromPantry(ingr_name):
                flash(f"Tried to remove amount from an ingredient not present in the pantry.","danger")
            else:
                if current_user.getIngredientAmount(ingr_name) < qty:
                    flash(f"Tried to remove more than is available in the pantry.","danger")
                else:
                    current_user.removeFromPantry(ingr_name, qty, units)

        # Setting an ingredient
        if add_ingr_form.set.data:
            current_user.setPantryIngredient(ingr_name, qty, date, units)
        
                
        return redirect(url_for("my_pantry"))
    all_ingr = PantryIngredient.query.filter_by(user_id=current_user.id).all()
    return render_template("pantry.html", title="My Pantry", add_form=add_ingr_form, all_ingr=all_ingr)


# Defines the delete ingredient function
# - Deletes the specified ingredient from the database
@app.route("/my_pantry/<int:ingredient_id>/delete", methods=["POST"])
@login_required
def delete_ingredient(ingredient_id):
    ingr = PantryIngredient.query.get_or_404(ingredient_id)
    if ingr.user_id != current_user.id:
        abort(403)
    current_user.deleteFromPantry(ingr.name)
    flash(f"{ingr.name} has been deleted!", "success")
    return redirect(url_for("my_pantry"))


# Defines the update recipe function
# - Renders the enter_recipe.html file and displays in browser, but already filled out with current recipe details
@app.route("/search_recipe/<int:recipe_id>/update", methods=["GET","POST"])
@login_required
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        abort(403)

    recipe_form = EnterRecipeForm()
    if recipe_form.validate_on_submit():
        recipe_name = recipe_form.recipe_name.data
        instructions = recipe_form.instructions.data
        ingredients = recipe_form.ingredients.data
        image = recipe_form.image.data
        image = image.read()
        if current_user.modifyRecipe(recipe, recipe_name, ingredients, instructions, image):
            flash(f"Recipe updated! You should now be able to search for the recipe in the search bar.","success")
            return redirect(url_for("search_recipe"))
        else:
            flash("Ingredients formatted incorrectly, try again","danger")
            return redirect(url_for("update_recipe",recipe_id=recipe.id))
    elif request.method == "GET":
        recipe_form.recipe_name.data = recipe.name
        recipe_form.instructions.data = recipe.instructions
        recipe_form.image.data = recipe.image
    return render_template("enter_recipe.html", title="Create a Recipe", form=recipe_form,
    legend="Update Recipe Information")


# Defines the delete recipe function
# - Deletes the recipe from the database
@app.route("/search_recipe/<int:recipe_id>/delete", methods=["GET","POST"])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    recipe_name = recipe.name
    if recipe.user_id != current_user.id:
        abort(403)
    current_user.deleteRecipe(recipe)
    flash(f"Recipe [{recipe_name}] deleted!", "success")
    return redirect(url_for("search_recipe"))

@app.route("/search_recipe/<int:recipe_id>/make", methods=["GET","POST"])
@login_required
def make_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id or recipe.canMake() == 0:
        abort(403)
    recipe.make()
    flash(f"Recipe [{recipe.name}] made!", "success")
    return redirect(url_for("search_recipe"))

