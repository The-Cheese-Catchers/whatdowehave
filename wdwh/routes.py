"""
Manages website routes
Connects front-end with back-end

This file acts as the VIEW and CONTROLLER in the MVC design pattern,
since it presents the data and handles form inputs to update the model

The View presents the model's data to the user.
The view knows how to access the model's data,
but it does not know what this data means or what
the user can do to manipulate it.

The Controller exists between the view and the model.
It listens to events triggered by the view (or another external source)
and executes the appropriate reaction to these events.
In most cases, the reaction is to call a method on the model.
Since the view and the model are connected through a notification mechanism,
the result of this action is then automatically reflected in the view.
"""
# pylint: disable=consider-using-f-string
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from wdwh import app, db, bcrypt
from wdwh.forms import (AddIngredientForm, EnterRecipeForm,
                        LoginForm, RegistrationForm, SearchRecipeForm)
from wdwh.models import User, PantryIngredient, RecipeIngredient, Recipe


@app.route("/")
@app.route("/home")
def home():
    """
    Defines the home page
    - Renders the home.html file and displays in browser
    """
    return render_template("home.html", title="Home")

@app.route("/register", methods=["GET","POST"])
def register():
    """
    Defines the registration page
    - Renders the registration.html file and displays in browser
    - Adds username and salted+hashed password to database
    - Redirects to home page when registration is complete
    """
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    register_form = RegistrationForm()
    if register_form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode()
        user = User(username=register_form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in!","success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=register_form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Defines the login page
    - Renders the login.html file and displays in browser
    - Checks if the username and the entered salted+hashed password are in the database
    - Redirects to homepage when login is complete
    """
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        flash("Login unsuccessful. Please check username and password.", "danger")
    return render_template("login.html", title="Login", form=login_form)

@app.route("/logout")
@login_required
def logout():
    """
    Defines the logout page
    - Logs out the user and redirects to the home page
    """
    logout_user()
    return redirect(url_for("home"))

@app.route("/enter_recipe", methods=["GET", "POST"])
@login_required
def enter_recipe():
    """
    Defines the enter recipe page
    - Renders the enter_recipe.html file and displays in browser
    - Allows user to update the recipe
    """
    recipe_form = EnterRecipeForm()
    if recipe_form.validate_on_submit():
        recipe_name = recipe_form.recipe_name.data
        instructions = recipe_form.instructions.data
        ingredients = recipe_form.ingredients.data

        if current_user.add_recipe(recipe_name, ingredients, instructions):
            flash("Recipe created! You should now be able to search \
                for the recipe in the search bar.","success")
            return redirect(url_for("search_recipe"))
        flash("Ingredients formatted incorrectly, try again","danger")
        recipe = Recipe.query.filter_by(name=recipe_name,user_id=current_user.id).first()
        return redirect(url_for("update_recipe",recipe_id=recipe.id))
    return render_template("enter_recipe.html", title="Create a Recipe", form=recipe_form,
    legend="Enter Recipe Information")

@app.route("/search_recipe", methods=["GET", "POST"])
@login_required
def search_recipe():
    """
    Defines the search recipe page
    - Renders the search_recipe.html file and displays in browser
    - Allows the user to search for many other recipes by querying an API
    """
    search_form = SearchRecipeForm()
    if search_form.validate_on_submit():
        # recipe_name = search_form.query.data
        # SEARCH API FOR THIS RECIPE AND LIST OUT DETAILS ON SEPARATE PAGE
        search_term = search_form.query.data
        searched_recipes = current_user.search_recipes(search_term)
        flash(f"Search results for {search_term}","success")
        return render_template("search_recipe.html", title="Search Recipe",
                form=search_form, recipes=searched_recipes, RecipeIngredient=RecipeIngredient)

    all_recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    return render_template("search_recipe.html", title="Search Recipe",
                form=search_form, recipes=all_recipes, RecipeIngredient=RecipeIngredient)

@app.route("/my_pantry", methods=["GET", "POST"])
@login_required
def my_pantry():
    """
    Defines the pantry page
    - Renders the my_pantry.html file and displays in browser
    - Displays each ingredient in a table with buttons to update or delete
    """
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
                current_user.add_to_pantry(ingr_name, qty, date, units)

        # Removing from the Pantry
        if add_ingr_form.remove.data:
            if not qty:
                flash("Can't remove without an amount","danger")
            if not current_user.get_ingredient_from_pantry(ingr_name):
                flash("Tried to remove amount from an ingredient not \
                    present in the pantry.","danger")
            else:
                if current_user.get_ingredient_amount(ingr_name) < qty:
                    flash("Tried to remove more than is available in the pantry.","danger")
                else:
                    current_user.remove_from_pantry(ingr_name, qty, units)

        # Setting an ingredient
        if add_ingr_form.set.data:
            current_user.set_pantry_ingredient(ingr_name, qty, date, units)

        return redirect(url_for("my_pantry"))
    all_ingr = PantryIngredient.query.filter_by(user_id=current_user.id).all()
    return render_template("pantry.html", title="My Pantry", add_form=add_ingr_form,
            all_ingr=all_ingr)

@app.route("/my_pantry/<int:ingredient_id>/delete", methods=["POST"])
@login_required
def delete_ingredient(ingredient_id):
    """
    Defines the delete ingredient function
    - Deletes the specified ingredient from the database
    """
    ingr = PantryIngredient.query.get_or_404(ingredient_id)
    if ingr.user_id != current_user.id:
        abort(403)
    current_user.delete_from_pantry(ingr.name)
    flash(f"{ingr.name} has been deleted!", "success")
    return redirect(url_for("my_pantry"))

@app.route("/search_recipe/<int:recipe_id>/update", methods=["GET","POST"])
@login_required
def update_recipe(recipe_id):
    """
    Defines the update recipe function
    - Renders the enter_recipe.html file and displays in browser,
      but already filled out with current recipe details
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        abort(403)

    recipe_form = EnterRecipeForm()
    if recipe_form.validate_on_submit():
        recipe_name = recipe_form.recipe_name.data
        instructions = recipe_form.instructions.data
        ingredients = recipe_form.ingredients.data

        if current_user.modify_recipe(recipe, recipe_name, ingredients, instructions):
            flash("Recipe updated! You should now be able to search for \
                the recipe in the search bar.","success")
            return redirect(url_for("search_recipe"))

        flash("Ingredients formatted incorrectly, try again","danger")
        return redirect(url_for("update_recipe",recipe_id=recipe.id))
    if request.method == "GET":
        recipe_form.recipe_name.data = recipe.name
        recipe_form.instructions.data = recipe.instructions
    return render_template("enter_recipe.html", title="Create a Recipe", form=recipe_form,
    legend="Update Recipe Information")

@app.route("/search_recipe/<int:recipe_id>/delete", methods=["GET","POST"])
@login_required
def delete_recipe(recipe_id):
    """
    Defines the delete recipe function
    - Deletes the recipe from the database
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    recipe_name = recipe.name
    if recipe.user_id != current_user.id:
        abort(403)
    current_user.delete_recipe(recipe)
    flash(f"Recipe [{recipe_name}] deleted!", "success")
    return redirect(url_for("search_recipe"))

@app.route("/search_recipe/<int:recipe_id>/make", methods=["GET","POST"])
@login_required
def make_recipe(recipe_id):
    """
    Defines the make recipe function
    - Makes the recipe using the pantry ingredients
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id or recipe.can_make() == 0:
        abort(403)
    recipe.make()
    flash(f"Recipe [{recipe.name}] made!", "success")
    return redirect(url_for("search_recipe"))
