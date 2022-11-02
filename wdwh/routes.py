import sqlite3
from sqlite3 import Error
from wdwh import app, db, bcrypt, db_functions
from wdwh.forms import *
from wdwh.models import User, load_user, load_user_from_username
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
        if db_functions.create_user(register_form.username.data, register_form.password.data):
            flash(f"Account created! Please login.","success")
            return redirect(url_for("login"))
        else:
            flash("Username already taken, please pick another one", "danger")
    return render_template("register.html", title="register", form=register_form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        if db_functions.validate_login(login_form.username.data, login_form.password.data):
            login_user(load_user_from_username(login_form.username.data), remember=login_form.remember.data)
            flash(f"Welcome back {login_form.username.data}!")
            return redirect(url_for("home"))
        else:
            flash("Login unsuccessful. Please check username and password.", "danger")
    return render_template("login.html", title="login", form=login_form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/enter_recipe", methods=["GET", "POST"])
def enter_recipe():
    recipe_form = EnterRecipeForm()
    if recipe_form.validate_on_submit():
        flash(f"Recipe created! You should now be able to search for the recipe in the search bar.","success")
        return redirect(url_for("home"))
    return render_template("enter_recipe.html", title="Create a Recipe", form=recipe_form)