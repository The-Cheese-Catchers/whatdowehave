from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)

PASSWORD = os.getenv("APP_PASSWORD")
PUBLIC_IP_ADDRESS = os.getenv("PUBLIC_IP_ADDRESS")
DBNAME = os.getenv("DBNAME")
PROJECT_ID = os.getenv("PROJECT_ID")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

ENV = "prod"


app.config["SECRET_KEY"] = "b'c\xd4T=@\xfckz\xdc\x1eP\xcc\x84\xd4\xadfC\x8fq$\xbb\x82\xab\x19'"
#app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
if ENV == 'dev':
    app.config["SQLALCHEMY_DATABASE_URI"]= "postgresql://postgres:root@localhost/test"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://ilqndltcvfcqgl:3b4300eea5c8e0692c301aa634a39cca95b750cb54d330b5f3c8ecff49f91304@ec2-44-195-132-31.compute-1.amazonaws.com:5432/d6tk7fgd8okbi4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

#since we are running one application, we do not need to do any thing fancy, just pass app into SQLAlchemy
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

'''
after starting up the instance, this will trigger, and if there is nothing
in the database, then we will create the tables and models that we have 
denoted in the models.py file

# To create tables: db.create_all()
# To delete tables: db.drop_all()
'''
@app.before_first_request
def create_tables():
    from wdwh.models import User,Recipe,Ingredient
    #db.drop_all()
    if db.inspect(db.engine).get_table_names() == []:
        print("create tables")
        db.create_all()

from wdwh import routes, models