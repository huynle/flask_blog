from flask_wtf import FlaskForm as Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length

from app.models import User


class EditForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])  # this validator is instantiated outside
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        """
        add to the Form.validate function and appending to the erro of the field when found and error.
        :return:
        """
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append("This nickname is already in use. Please choose another one.")
            return False
        return True


class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])


class LoginForm(Form):
    ## each of the field here has an attribute 'data'
    openid = StringField('openid', validators=[DataRequired()])  # NOTE: this way of validating the data!!
    remember_me = BooleanField("remember_me", default=False)
    submit_name = "FOOBAR"

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])