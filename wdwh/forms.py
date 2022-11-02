from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from wdwh.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class EnterRecipeForm(FlaskForm):
    recipe_name = StringField("Recipe Name", validators=[DataRequired()])
    ingredients = TextAreaField(
        "Enter ingredients, separated by a comma (,)", validators=[DataRequired()]
    )
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
    query = StringField("Search for Recipe", validators=[DataRequired()])
    submit = SubmitField("Submit")