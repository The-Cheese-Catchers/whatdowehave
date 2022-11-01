import json
import bcrypt
from wdwh import cryp_salt

USERS_JSON_PATH = "wdwh/data/users.json"

"""
    Returns user json as a python dictionary
"""
def readUsers():
    users_json_file = open(USERS_JSON_PATH)
    users_json = json.load(users_json_file)
    users_json_file.close()

    return users_json

"""
    Checks whether a login is valid
"""
def checkLogin(entered_username, entered_password):
    users_json = readUsers()

    if (entered_username not in users_json.keys()):
        return False
    return bcrypt.checkpw(entered_password.encode(), users_json[entered_username].encode())

"""
    Register a new user
        returns True if new user is successfully added
        returns False if username is already taken
"""
def registerUser(entered_username, entered_password):
    users_json = readUsers()

    if (entered_username in users_json.keys()):
        return False

    hashed_entered_password = bcrypt.hashpw(entered_password.encode(), cryp_salt).decode()
    users_json[entered_username] = hashed_entered_password

    users_json_file = open(USERS_JSON_PATH, "w+")
    users_json_file.write(json.dumps(users_json, indent = 4))
    users_json_file.close()
    return True
