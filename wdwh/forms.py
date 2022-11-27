from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from wdwh.models import User, Ingredient, PantryIngredient, RecipeIngredient


# Registration data form
# - Defines the datatypes and variables for each input box the user interacts with when registering
# - Has a method to validate whether the inputted username is taken or not (username must be unique)
class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')


# Login data form
# - Defines the datatypes and variables for each input box the user interacts with when logging in
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


# Adding ingredient data form
# - Defines the datatypes and variables for each input box the user interacts with when adding an ingredient
# - Has a method to validate whether user enters impossible amount (0 or negative ingredients)
class AddIngredientForm(FlaskForm):
    ingr_name = StringField("Ingredient Name", validators=[DataRequired()])
    qty = IntegerField("Amount", validators=[Optional()])
    date = DateField("Expiration Date", validators=[Optional()])
    units = StringField("Unit", validators=[Optional()])
    add = SubmitField("Add")
    remove = SubmitField("Remove")
    set = SubmitField("Set")

    def validate_qty(self, qty):
        if qty.data < 1:
            raise ValidationError('Improper amount.')


# Custom recipe data form
# - Defines the datatypes and variables for each input box the user interacts with when entering a recipe
class EnterRecipeForm(FlaskForm):
    recipe_name = StringField("Recipe Name", validators=[DataRequired()])
    ingredients = TextAreaField("Ingredients: enter name, amount followed by a ; example: Eggs, 4; Milk, 1",
        validators=[DataRequired()])
    # ingredients = FieldList(FormField(AddIngredientForm),min_entries=1)
    
    instructions = TextAreaField(
        "Write some instructions on how to make this recipe",
        validators=[DataRequired()],
    )
    image = FileField(
        "Upload a picture of the finished product",
        validators=[FileAllowed(["jpg", "png"])],
    )
    make_public = BooleanField("Make Recipe Public")
    submit = SubmitField("Submit")

# Searching a recipe form
# - Defines the datatypes and variables for each input box the user interacts with when searching for a recipe
class SearchRecipeForm(FlaskForm):
    query = StringField("Search for Recipe", validators=[DataRequired()])
    submit = SubmitField("Search")
            
