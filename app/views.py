"""
Each view function is mapped to one or more request URLS.

"""
from datetime import datetime

from flask import flash
from flask import g  # global setup by Flask as a place to store and share data during the life of a request
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import login_user, current_user, login_required, logout_user

# This 'app' is the actual object itself that was initiated when the module 'app' got initiated
from app import app, oid, db, lm
from app.forms import LoginForm, EditForm, PostForm, SearchForm
from app.models import User, Post
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required  # decorated with the flask_login extension
def index(page=1):
    form = PostForm()
    # user = {'nickname': 'Huy'}  # fake user
    if form.validate_on_submit():
        post = Post(body=form.post.data,
                    timestamp=datetime.utcnow(),
                    author=g.user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live!")
        return redirect(url_for('index'))  # redirect itself back to see the updated post
        #  This redirect is important because it prevents the app from POSTing a second time by pressing refresh
    # user = g.user

    # posts = [  # fake array of posts
    #     {
    #         'author': {'nickname': 'John'},
    #         'body': 'Beautiful day in Portland!'
    #     },
    #     {
    #         'author': {'nickname': 'Susan'},
    #         'body': 'The Avengers movie was so cool!'
    #     }
    # ]
    # posts = g.user.followed_posts().all()
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)

    return render_template('index.html',  # render_template
                           title="Home",
                           posts=posts,
                           form=form)


#  POST requests. Default is GET
@app.route("/login", methods=['GET', 'POST'])  # the methods tells flask that this view function accepts both GET and
@oid.loginhandler  # this tells flask-openid that this is the login function view
def login():
    # does this handle the auto login? if g.user is present?
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


@app.before_request
def before_request():
    """
    This is important to note. the 'User' and its relation to the 'g' variable

    the 'g' global variable persists for a request. So before the request can be initiated, this sets the 'g'
    variable for us to reference to and use

    :return:
    """
    g.user = current_user  # global for flask-login
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()


@lm.user_loader  #
def load_user(id):
    """
    this lm -> referenced to LoginManager from Flask-Login
    the function 'load_user' is registered to flask-login by the use of this decorator

    :param id:
    :return:
    """
    return User.query.get(int(id))


@app.route("/user/<nickname>")  # this route is referenced in the template by '{{ url_for('user',
# nickname=g.user.nickname}}'
@app.route("/user/<nickname>/<int:page>")
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()  # user here is an object with attributes of nickname
    if user is None:
        flash("User {} for found".format(nickname))
        return redirect(url_for('index'))
    # posts = g.user.followed_posts().all()
    posts = user.sorted_posts().paginate(page, POSTS_PER_PAGE, False)
    # posts = [
    #     {'author': user, 'body': "Test post body #1"},
    #     {'author': user, 'body': "Test post body #2"}
    # ]
    return render_template('user.html',
                           user=user,
                           posts=posts)


# function is called after OpenID try to login
@oid.after_login
def after_login(resp):
    #  validation of the email
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        #  if is not a valid email, we will not allow for login
        return redirect(url_for('login'))
    # find in database for the email provided
    user = User.query.filter_by(email=resp.email).first()
    if user is None:  # if not User if found, the user will then be considered a new User and will be added to the DB
        nickname = resp.nickname
        if nickname is None or nickname == "":  # solve cases for some OpenID does not provide user name
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)  # this solves the unique nickname problem by incrementing the
        #  number
        user = User(nickname=nickname, email=resp.email)  # There's a problem here with unique nickname
        db.session.add(user)
        db.session.commit()
        # make the user follower himself/herself
        db.session.add(user.follow(user))
        db.session.commit()

    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/edit', methods=['POST', 'GET'])
@login_required
def edit():
    """
    Edit allows the user to edit their profile after being logged in
    note the user of the g variable
    :return:
    """
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash("Your changes have been saved!")
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.route("/follow/<nickname>")
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash("User {} not found.".format(nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash("You can't follow yourself!")
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow {}.'.format(nickname))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash("You are not following {}.".format(nickname))
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash("User {} not found.".format(nickname))
    if user == g.user:
        flash("You can't unfollow yourself!")
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """
    If this is triggered by the database error, then the DB session will be in an invalid state, rollback is needed
    to a working session
    :param error:
    :return:
    """
    db.session.rollback()
    return render_template('500.html'), 500


@app.route("/search", methods=["POST"])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):

    # results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    results = []
    return render_template('search_results.html',
                           query=query,
                           results=results)


@app.route('/err')
def err():
    raise Exception
