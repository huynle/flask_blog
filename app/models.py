from app import db


class User(db.Model):
    """
    model for all users to be stored in DB

    """
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

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
        # try:
        #     return unicode(self.id)  # python 2
        # except NameError:
        return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Post(db.Model):
    """
    NOTE the db.ForeignKey, this looks at the user table for its ID

    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)