from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "e030a8c3cbfc01c4a941a37f0d527d19"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy()
db.init_app(app)

# if db.inspect(db.engine).get_table_names() == []:
#     db.create_all()
# To create table: db.create_all()
# To delete table: db.drop_all()

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from wdwh import routes