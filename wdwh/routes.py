import sqlite3
from sqlite3 import Error
from wdwh import app, db, bcrypt
from wdwh.forms import *
from wdwh.models import User, Ingredient, Pantry, Recipe
from flask import Flask, render_template, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required

def create_connection(db_file):
    cnxn = None
    try:
        cnxn = sqlite3.connect(db_file)
        return cnxn
    except Error as e:
        print(e)
        quit()

@app.route("/")
@app.route("/home")
def home():
    p_data = [[]]
    return render_template("home.html", title="home", p=p_data)

@app.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        # Add account information to database
        hashed_pw = bcrypt.generate_password_hash(register_form.password.data).decode("utf-8")
        user = User(username=register_form.username.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f"Account created! Please login.","success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=register_form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        # Check database if username/password combo are valid
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            flash(f"Welcome back!")
            return redirect(url_for("home"))
        else:
            flash("Login unsuccessful. Please check username and password.", "danger")
    return render_template("login.html", title="login", form=login_form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/enter_recipe")
def enter_recipe():
    recipe_form = EnterRecipeForm()
    if recipe_form.validate_on_submit():
        flash(f"Recipe created! You should now be able to search for the recipe in the search bar.","success")
        return redirect(url_for("home"))
    return render_template("enter_recipe.html", title="Create a Recipe", form=recipe_form)