from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from wdwh.models import User, Ingredient, PantryIngredient, RecipeIngredient


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


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class AddIngredientForm(FlaskForm):
    ingr_name = StringField("Ingredient Name", validators=[DataRequired()])
    qty = IntegerField("Amount", validators=[DataRequired()])
    date = DateField("Expiration Date", validators=[Optional()])
    add = SubmitField("Add")
    remove = SubmitField("Remove")

    def validate_qty(self, qty):
        if qty.data < 1:
            raise ValidationError('Improper amount.')

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


class SearchRecipeForm(FlaskForm):
    query = StringField("Search for Recipe", validators=[DataRequired()])
    submit = SubmitField("Search")
            
