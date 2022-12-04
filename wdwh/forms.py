"""
This file manages all the HTML forms used to collect user data
"""
# pylint: disable=consider-using-f-string
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField,
                    BooleanField, TextAreaField, IntegerField, DateField)
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from wdwh.models import User


class RegistrationForm(FlaskForm):
    """
    Registration data form
    - Defines the datatypes and variables for each input
      box the user interacts with when registering
    - Has a method to validate whether the inputted username is
      taken or not (username must be unique)
    """
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        """ Checks if a username has already been taken """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    """
    Login data form
    - Defines the datatypes and variables for each input box the
      user interacts with when logging in
    """
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class AddIngredientForm(FlaskForm):
    """
    Adding ingredient data form
    - Defines the datatypes and variables for each input box the user
      interacts with when adding an ingredient
    - Has a method to validate whether user enters impossible amount (0 or negative ingredients)
    """
    ingr_name = StringField("Ingredient Name", validators=[DataRequired()])
    qty = IntegerField("Amount", validators=[Optional()])
    date = DateField("Expiration Date", validators=[Optional()])
    units = StringField("Unit", validators=[Optional()])
    add = SubmitField("Add")
    remove = SubmitField("Remove")
    set = SubmitField("Set")

    def validate_qty(self, qty):
        """ Validates the qty entered by users """
        if qty.data < 1:
            raise ValidationError('Improper amount.')

class ExpirationDateForm(FlaskForm):
    date = DateField("Expiration Date", validators=[Optional()])
    add = SubmitField("Set")

class EnterRecipeForm(FlaskForm):
    """
    Custom recipe data form
    - Defines the datatypes and variables for each input box the
      user interacts with when entering a recipe
    """
    recipe_name = StringField("Recipe Name", validators=[DataRequired()])
    ingredients = TextAreaField(
        "Ingredients: enter name, amount followed by a ; example: Eggs, 4; Milk, 1",
        validators=[DataRequired()])

    instructions = TextAreaField(
        "Write some instructions on how to make this recipe",
        validators=[DataRequired()],
    )
    picture = FileField(
        "Upload a picture of the finished product",
        validators=[FileAllowed(["jpg", "png"])],
    )
    make_public = BooleanField("Make Recipe Public")
    submit = SubmitField("Submit")

class SearchRecipeForm(FlaskForm):
    """
    Searching a recipe form
    - Defines the datatypes and variables for each input box the
      user interacts with when searching for a recipe
    """
    query = StringField("Search for Recipe", validators=[DataRequired()])
    submit = SubmitField("Search")
