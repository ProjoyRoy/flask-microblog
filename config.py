import os
from datetime import timedelta


WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
REMEMBER_COOKIE_DURATION = timedelta(days=365)

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '1478267859147820',
        'secret': '7aa567d383b609c83cb8fc6002053ae1'
    },
    'twitter': {
        'id': '3RzWQclolxWZIMq5LJqzRZPTl',
        'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
    }
}
