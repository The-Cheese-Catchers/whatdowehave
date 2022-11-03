import sqlite3
from sqlite3 import Error
from wdwh import app, db, bcrypt, db_functions
from wdwh.forms import *
from wdwh.models import User, Ingredient
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    # if current_user.is_authenticated:
    #     return redirect(url_for("my_pantry"))
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
        flash(f"Recipe created! You should now be able to search for the recipe in the search bar.","success")
    return render_template("enter_recipe.html", title="Create a Recipe", form=recipe_form)


@app.route("/search_recipe", methods=["GET", "POST"])
@login_required
def search_recipe():
    search_form = SearchRecipeForm()
    if search_form.validate_on_submit():
        recipe_name = search_form.query.data
        # SEARCH API FOR THIS RECIPE AND LIST OUT DETAILS ON SEPARATE PAGE
    return render_template("search_recipe.html", title="Search Recipe", form=search_form)


@app.route("/my_pantry", methods=["GET", "POST"])
@login_required
def my_pantry():
    """
        TODO:
        - Make Ingredients and User class (for OOP)
        - Make delete button on my pantry page to delete ingredients
    """
    add_ingr_form = AddIngredientForm()
    if add_ingr_form.validate_on_submit():
        # Capitalize all ingredients
        ingr_name = add_ingr_form.name.data.capitalize()
        qty = add_ingr_form.qty.data

        # Adding to the Pantry
        if add_ingr_form.add.data:
            current_user.addToPantry(ingr_name, qty)
        # Removing from the Pantry
        if add_ingr_form.remove.data:
            if not current_user.getIngredientFromPantry(ingr_name):
                flash("Tried to remove amount from ingredient not in pantry.", "danger")
            else:
                if current_user.getIngredientAmount(ingr_name) < qty:
                    flash("Tried to remove a higher amount than present in the pantry.", "danger")
                else:
                    current_user.removeFromPantry(ingr_name, qty)
        # Deleting item from the Pantry
        if add_ingr_form.delete.data:
            if not current_user.getIngredientFromPantry(ingr_name):
                flash("Tried to delete an ingredient not in pantry.", "danger")
            else:
                current_user.deleteFromPantry(ingr_name)
                
        return redirect(url_for("my_pantry"))
    all_ingr = Ingredient.query.filter_by(user_id=current_user.id).all()
    return render_template("pantry.html", title="My Pantry", add_form=add_ingr_form, all_ingr=all_ingr)