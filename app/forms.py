from flask_wtf import FlaskForm as Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(Form):
    ## each of the field here has an attribute 'data'
    openid = StringField('openid', validators=[DataRequired()])  # NOTE: this way of validating the data!!
    remember_me = BooleanField("remember_me", default=False)
    submit_name = "FOOBAR"