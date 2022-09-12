# Standard Library Imports
import sqlite3
from sqlite3 import Error

# Local File Imports
from forms.forms import *

# Third Party Imports
from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "e030a8c3cbfc01c4a941a37f0d527d19"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f"User {self.username}"

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    family = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    subtype = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f"{self.family}, {self.subtype} {self.name}"

class Pantry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    ingredients = db.relationship('Ingredient', backref='FoundIn', lazy=True)
    
    def __repr__(self):
        return f"{self.user_id} has {self.quantity} units of {self.ingredient_id}"

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    
    def __repr__(self):
        return f"{self.name}"

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
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        # Add account information to database
        flash(f"Account created! Please login.","success")
        return redirect(url_for("home"))
    return render_template("register.html", title="register", form=register_form)

@app.route("/login")
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        flash(f"Welcome back!")
        return redirect(url_for("home"))
    return render_template("login.html", title="login", form=login_form)