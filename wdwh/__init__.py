from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)

DBCONNSTRING = os.getenv("DB_CONN")
SECRET_KEY = os.getenv("SECRET_KEY")
ENV_TYPE = os.getenv("ENV_TYPE")

ENV = ENV_TYPE


app.config["SECRET_KEY"] = SECRET_KEY
#app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
if ENV_TYPE == 'prod':
    app.config["SQLALCHEMY_DATABASE_URI"]= DBCONNSTRING
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:root@localhost/test"
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
