from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

PASSWORD ="weGotFoodAtHome"
PUBLIC_IP_ADDRESS ="35.230.188.245"
DBNAME ="testing"
PROJECT_ID ="wegotfoodathome"
INSTANCE_NAME ="wgfah"


app.config["SECRET_KEY"] = "b'c\xd4T=@\xfckz\xdc\x1eP\xcc\x84\xd4\xadfC\x8fq$\xbb\x82\xab\x19'"
app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True


db = SQLAlchemy(app)
# To create table: db.create_all()
# To delete table: db.drop_all()

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@app.before_first_request
def create_tables():
    from wdwh.models import User,Recipe,Ingredient

    db.create_all()

from wdwh import routes, models