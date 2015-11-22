from app import db, lm
from config import SECRET_KEY, REMEMBER_COOKIE_DURATION
from flask.ext.login import UserMixin
from werkzeug import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from hashlib import md5


token_serializer = URLSafeTimedSerializer(SECRET_KEY)


@lm.token_loader
def load_token(token):
    max_age = REMEMBER_COOKIE_DURATION.total_seconds()

    # Decrypt the Security Token, data = [userid, hashpass]
    data = token_serializer.loads(token, max_age=max_age)

    # Find the User
    user = User.query.get(data[0])

    # Check pwdhash and return user or None
    if user and data[1] == user.pwdhash:
        return user
    return None


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    pwdhash = db.Column(db.String(64), nullable=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    def __init__(self, username, email, password=None, about_me=None):
        self.username = username.title()
        if email is not None:
            self.email = email.lower()
        if password is not None:
            self.set_password(password)
        self.about_me = about_me

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def get_auth_token(self):
        data = [str(self.id), self.pwdhash]
        return token_serializer.dumps(data)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
            (md5(self.email.encode('utf-8')).hexdigest(), size)

    def has_password(self):
        if self.pwdhash is None:
            return False
        else:
            return True

    @staticmethod
    def create_unique_username(username):
        username = username.title()
        if User.query.filter_by(username=username).first() is None:
            return username
        version = 2
        while True:
            new_username = username + str(version)
            if User.query.filter_by(username=new_username).first() is None:
                break
            version += 1
        return new_username

    def __repr__(self):
        return '<User %r>' % (self.email)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
