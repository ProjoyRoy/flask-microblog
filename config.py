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
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = secrets.MAIL_USERNAME
MAIL_PASSWORD = secrets.MAIL_PASSWORD

# administrator list
ADMINS = secrets.ADMINS

# pagination
POSTS_PER_PAGE_INDEX = 3
POSTS_PER_PAGE_PROFILE = 5

# WHOOSH database
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50
