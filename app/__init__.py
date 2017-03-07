import os

from flask import Flask
from flask_openid import OpenID
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# create an application object
from config import basedir

app = Flask(__name__)
app.config.from_object('config')  # why is this coming from 'config' object?

db = SQLAlchemy(app)

# this app is different from the 'app' above.. this is the app module for which we will import views from
from app import views, models
# the views are the handlers that response to requests from web browser or other clients

lm = LoginManager()
lm.init_app(app)
oid = OpenID(app, os.path.join(basedir, "tmp"))