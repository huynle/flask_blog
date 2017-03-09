import os

from flask import Flask
from flask_openid import OpenID  # this takes care of the identification and getting the ID for the user
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager  # takes care of the inputs and user handling

# create an application object
from config import basedir, MAIL_PASSWORD, MAIL_USERNAME, MAIL_PORT, MAIL_SERVER, ADMINS

app = Flask(__name__)
app.config.from_object('config')  # why is this coming from 'config' object?

# SQLAlchemy is Python SQL toolkit and Object Relational Mapper
db = SQLAlchemy(app)
# the views are the handlers that response to requests from web browser or other clients

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'  # this is the view that logs the user in
oid = OpenID(app, os.path.join(basedir, "tmp"))

# enabling email to be sent when there is an error
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, "app failure", credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


# enable logging to a file
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1*1024*1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')


# this app is different from the 'app' above.. this is the app module for which we will import views from
from app import views, models