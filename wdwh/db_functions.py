import json
import bcrypt
from wdwh import cryp_salt, login_manager
from flask_login import UserMixin

DB_PATH = "wdwh/data.json"

def load_data():
    """
        Loads the database and returns the data in a dictionary
    """
    data_file = open(DB_PATH, 'r')
    json_data_file = json.load(data_file)
    data_file.close()
    return json_data_file


def create_user(username, password):
    """
        Inserts a new user into the database with the given username/password combination
    """
    data = load_data()
    
    if username in data.keys():
        return False
    
    hashed_password = bcrypt.hashpw(password.encode(), cryp_salt).decode()
    data[username] = {
        "id" : len(data) + 1,
        "password" : hashed_password,
        "pantry" : {}
    }
    
    data_file = open(DB_PATH, 'w+')
    json_dumpfile = json.dumps(data, indent=4)
    data_file.write(json_dumpfile)
    data_file.close()
    
    return True


def validate_login(username, password):
    """
        Validates the login request by checking if the given username/password combination is in the database
    """
    data = load_data()
    
    if username not in data.keys():
        return False
    
    return bcrypt.checkpw(password.encode(), data[username]["password"].encode())