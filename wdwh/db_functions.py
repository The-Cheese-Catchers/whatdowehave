import json
import bcrypt
from wdwh import cryp_salt, login_manager
from flask_login import UserMixin

DB_PATH = "wdwh/data.json"

def load_data():
    """
    Loads the database and returns the data in a dictionary
    """
    with open(DB_PATH, 'r') as data_file:
        json_data_file = json.load(data_file)
        
    return json_data_file

def save_data(new_data):
    """
        Saves by overwriting the json file
    """
    data_file = open(DB_PATH, 'w+')
    json_dumpfile = json.dumps(new_data, indent=4)
    data_file.write(json_dumpfile)
    data_file.close()


def create_user(username: str, password: str) -> bool:
    """
    Inserts a new user into the database with the given username/password combination
    """
    data = load_data()
    
    if username in data.keys():
        return False
    
    hashed_password = bcrypt.hashpw(password.encode(), cryp_salt).decode()
    user_data = {
        "id" : len(data) + 1,
        "username" : username,
        "password" : hashed_password,
        "pantry" : {},
        "recipes" : {}
    }
    data[username] = user_data
    
    with open(DB_PATH, 'w+') as data_file:
        json_dumpfile = json.dumps(data, indent=4)
        data_file.write(json_dumpfile)
    
    return True


def validate_login(username: str, password: str) -> bool:
    """
    Validates the login request by checking if the given username/password combination is in the database
    """
    data = load_data()
    
    if username not in data.keys():
        return False
    
    return bcrypt.checkpw(password.encode(), data[username]["password"].encode())

def addRecipe(username, recipe_form):
    data = load_data()

    recipes = data[username]["recipes"]

    recipe_name = recipe_form.recipe_name.data

    if recipe_name in recipes.keys():
        return False

    recipe_details = {
        "ingredients" : recipe_form.ingredients.data,
        "instructions" : recipe_form.instructions.data
        # TO DO: add picure
    }

    recipes[recipe_name] = recipe_details

    save_data(data)
    return True
