import sqlite3
from sqlite3 import Error
from wdwh import app, db, bcrypt
from wdwh.forms import *
from wdwh.models import User, PantryIngredient, RecipeIngredient, Recipe
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home")

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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/enter_recipe", methods=["GET", "POST"])
@login_required
def enter_recipe():
    recipe_form = EnterRecipeForm()
    if recipe_form.validate_on_submit():
        recipe_name = recipe_form.recipe_name.data
        instructions = recipe_form.instructions.data
        ingredients = recipe_form.ingredients.data

        if current_user.addRecipe(recipe_name, ingredients, instructions):
            flash(f"Recipe created! You should now be able to search for the recipe in the search bar.","success")
            return redirect(url_for("search_recipe"))
        else:
            flash("Ingredients formatted incorrectly, try again","danger")
            recipe = Recipe.query.filter_by(name=recipe_name,user_id=current_user.id).first()
            return redirect(url_for("update_recipe",recipe_id=recipe.id))
    return render_template("enter_recipe.html", title="Create a Recipe", form=recipe_form,
    legend="Enter Recipe Information")


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


@app.route("/my_pantry", methods=["GET", "POST"])
@login_required
def my_pantry():
    add_ingr_form = AddIngredientForm()
    if add_ingr_form.validate_on_submit():
        # Capitalize all ingredients
        ingr_name = add_ingr_form.ingr_name.data.capitalize()
        qty = add_ingr_form.qty.data
        date = add_ingr_form.date.data

        # Adding to the Pantry
        if add_ingr_form.add.data:
            current_user.addToPantry(ingr_name, qty, date)

        # Removing from the Pantry
        if add_ingr_form.remove.data:
            if not current_user.getIngredientFromPantry(ingr_name):
                flash(f"Tried to remove amount from an ingredient not present in the pantry.","danger")
            else:
                if current_user.getIngredientAmount(ingr_name) < qty:
                    flash(f"Tried to remove more than is available in the pantry.","danger")
                else:
                    current_user.removeFromPantry(ingr_name, qty)
        
                
        return redirect(url_for("my_pantry"))
    all_ingr = PantryIngredient.query.filter_by(user_id=current_user.id).all()
    return render_template("pantry.html", title="My Pantry", add_form=add_ingr_form, all_ingr=all_ingr)

@app.route("/my_pantry/<int:ingredient_id>/delete", methods=["POST"])
@login_required
def delete_ingredient(ingredient_id):
    ingr = PantryIngredient.query.get_or_404(ingredient_id)
    if ingr.user_id != current_user.id:
        abort(403)
    current_user.deleteFromPantry(ingr.name)
    flash(f"{ingr.name} has been deleted!", "success")
    return redirect(url_for("my_pantry"))

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

        if current_user.modifyRecipe(recipe, recipe_name, ingredients, instructions):
            flash(f"Recipe updated! You should now be able to search for the recipe in the search bar.","success")
            return redirect(url_for("search_recipe"))
        else:
            flash("Ingredients formatted incorrectly, try again","danger")
            return redirect(url_for("update_recipe",recipe_id=recipe.id))
    elif request.method == "GET":
        recipe_form.recipe_name.data = recipe.name
        recipe_form.instructions.data = recipe.instructions
    return render_template("enter_recipe.html", title="Create a Recipe", form=recipe_form,
    legend="Update Recipe Information")

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

