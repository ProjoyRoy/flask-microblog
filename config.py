import os
import secrets
from datetime import timedelta

WTF_CSRF_ENABLED = True
SECRET_KEY = secrets.SECRET_KEY
REMEMBER_COOKIE_DURATION = timedelta(days=365)

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

OAUTH_CREDENTIALS = secrets.OAUTH_CREDENTIALS

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['you@example.com']

# pagination
POSTS_PER_PAGE_INDEX = 3
POSTS_PER_PAGE_PROFILE = 5
