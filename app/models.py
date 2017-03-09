"""
When attribute of a model class is changed or updated, db_migrate.py script should be ran to keep everything updated
in the DB.

"""

from app import db, app
from hashlib import md5

# getting full text search working
import sys

if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask_whooshalchemy as whooshalchemy

# this is a auxiliary table that has no data other than foreign keys
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model):
    """
    model for all users to be stored in DB

    """
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    # this new relationship is called followed
    followed = db.relationship('User',  # initiate a relationship and linking to self (User) to 'User' instances
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),  # since 'followers' is not a model,
                               # the odd syntax is used to get the field name
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')  # returns the actual query object, and NOT the result of the query

    # itself

    def follow(self, user):
        """
        returns None when fail

        :param user:
        :return:
        """
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def sorted_posts(self):
        """
        getting the user posts that in order.. this case would use 'self', when trying to get ALL the posts,
        use 'Post' instead
        :return:
        """
        return self.posts.order_by(Post.timestamp.desc())

    def is_following(self, user):
        """
        checks the association table to see if there the following # is greater than zero

        the 'follow' relationship will return all the {follower, followed) pairs. Then this is filtered

        :param user:
        :return:
        """
        #  because self.followed has a lazy='dynamic' setting, the query object is returned and NOT the results of the
        #  query itself
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """
        This query has three parts, join, filter and order_by
        :return:
        """
        #  this method returns a query object and NOT the result, similar to 'lazy' = 'dynamic' in relationship
        #  this is good practice since the caller can tach on additional queries
        return Post.query.join(followers,
                               (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    @property
    def is_authenticated(self):
        """
        should or should not allow to authenticate. NOT is the specific user authenticated

        :return:
        """
        return True

    @property
    def is_active(self):
        """
        should not should not allow user to be active; eg. banned or not. NOT the specific user being active.

        :return:
        """
        return True

    @property
    def is_anonymous(self):
        """
        Allowing fake user to log into the system or not

        :return:
        """
        return False

    def get_id(self):
        return str(self.id)  # python 3

    def avatar(self, size):
        """
        by using a method to return the avatar image, this allows us to update this function later if gravatar is not used in the future
        :param size:
        :return:
        """
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return None
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Post(db.Model):
    """
    NOTE the db.ForeignKey, this looks at the user table for its ID

    """
    __searchable__ = ['body']  # array of datafield that can be search in the posts

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)


if enable_search:
    whooshalchemy.whoosh_index(app, Post)
