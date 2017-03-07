"""
Each view function is mapped to one or more request URLS.

"""
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for

from app import app, lm, \
    oid  # This 'app' is the actual object itself that was initated when the module 'app' got initiated
from app.forms import LoginForm
from app.models import User


@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Huy'}  # fake user
    posts = [  # fake array of posts
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',  # render_template
                           title="Home",
                           posts=posts,
                           user=user)


@app.route("/login", methods=['GET', 'POST'])  # the methods tells flask that this view function accepts both GET and
@oid.loginhandler
#  POST requests. Default is GET
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))


    form = LoginForm()  # gets the object and instantiate it, the template then have access to the 'openid' and
    # 'remember_me' attributes of the object

    if form.validate_on_submit():  # uses the validator specified in the form object creation
        # returns a False if the fields has not been input when this handler is called

        # flash('Login requested for OpenID:"%s", remember_me="%s' %
        #       (form.openid.data, str(form.remember_me.data)))
        #  flash is being used here for debug, but in production it is useful for user feedback
        #  the flash messages have to be explicitly referenced in the template!!! use 'get_flashed_messages()
        #  these messages are removed from the message list once used?
        # return redirect('/index')  # if all is successful, navi to the index page

        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=["nickname", "email"])

    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config["OPENID_PROVIDERS"]
                           )

@lm.user_loader
def load_user(id):
    """
    this lm -> referenced to LoginManager from Flask-Login
    the function 'load_user' is registered to flask-login by the use of this decorator

    :param id:
    :return:
    """
    return User.query.get(int(id))


@app.route('/err')
def err():
    raise Exception
