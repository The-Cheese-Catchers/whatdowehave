from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
import bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "e030a8c3cbfc01c4a941a37f0d527d19"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

cryp_salt = bcrypt.gensalt()
# bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from wdwh import routes