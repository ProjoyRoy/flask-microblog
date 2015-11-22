#!/home/pj/.conda/envs/flask-microblog/bin/python
import os
import unittest

from unittest import TestCase
from flask import url_for
from config import basedir
from app import app, db
from app.models import User
from flask.ext.login import login_user, logout_user, current_user

grav_url = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'


class BaseTestClass(TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')

        self.app = app
        self.client = self.app.test_client()
        self._ctx = self.app.test_request_context()
        self._ctx.push()
        db.create_all()

    def tearDown(self):
        if self._ctx is not None:
            self._ctx.pop()
        db.session.remove()
        db.drop_all()


class UserTestClass(BaseTestClass):

    def create_user(self, user):
        db.session.add(user)
        db.session.commit()

    def signup(self, username, email, password):
        return self.client.post(url_for('signup'), data=dict(
            username=username,
            email=email,
            password=password
        ), follow_redirects=True)

    def login(self, user, email, password):
        if current_user.is_anonymous:
            if user.email == email and user.check_password(password):
                login_user(user)
        return self.client.post(url_for('login'), data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def edit(self, user, username, email, password, about_me):
        return self.client.post(url_for('edit'), data=dict(
            username=username,
            email=email,
            password=password,
            about_me=about_me
        ), follow_redirects=True)

    def logout(self):
        logout_user()
        return self.client.get(url_for('logout'), follow_redirects=True)


class UserTests(UserTestClass):

    def test_create_unique_username(self):
        u = User(username='neo', email='neo@one.com')
        self.create_user(u)
        username = User.create_unique_username('neo')
        assert username != 'neo'

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = grav_url
        assert avatar[0:len(expected)] == expected

    def test_signup_path(self):
        assert current_user.is_anonymous
        rv = self.signup('Rambo', 'rambo@test.com', 'foobar')
        assert 'User: Rambo' in rv.data.decode("utf-8")

    def test_login_and_logout(self):
        u = User(username='john', email='john@example.com', password='foobar')
        self.create_user(u)
        assert u in db.session  # test that user was created in db
        assert current_user.is_anonymous  # test that no one is logged in

        # test login with invalid email
        rv = self.login(u, 'james@example.com', 'foobar')
        assert 'No such email' in rv.data.decode("utf-8")
        assert current_user.is_anonymous

        # test login with invalid password
        rv = self.login(u, 'john@example.com', 'fakepass')
        assert 'Incorrect password' in rv.data.decode("utf-8")
        assert current_user.is_anonymous

        # test login with valid credentials
        rv = self.login(u, 'john@example.com', 'foobar')
        assert current_user.is_active
        assert u == current_user
        assert 'User: John' in rv.data.decode("utf-8")

        # while logged in, test that going to login or signup
        # takes user to index page
        newuser = User(username='bonehead',
                       email='bone@head.com', password='foobar')
        rv = self.login(newuser, 'bone@head.com', 'foobar')
        assert 'Already logged in.' in rv.data.decode("utf-8")
        assert u == current_user
        rv = self.signup('bonehead', 'bone@head.com', 'foobar')
        assert 'Need to log out before signing up.' in rv.data.decode("utf-8")
        assert u == current_user

        # test logout
        assert current_user.is_active
        rv = self.logout()
        assert 'index' in rv.data.decode("utf-8")
        assert current_user.is_anonymous

    def test_edit(self):
        u = User(username='jim', email='jim@example.com', password='foobar',
                 about_me='test')
        self.create_user(u)
        assert u in db.session

        # going to the edit page when no one is logged in
        assert current_user.is_anonymous
        rv = self.edit(u, 'james', 'james@example.com', 'foobar', 'test')
        assert "Please log in to access this page" in rv.data.decode("utf-8")

        # loggin in test user
        self.login(u, 'jim@example.com', 'foobar')
        assert current_user == u

        # checking empty edit
        rv = self.edit(u, '', '', '', '')
        assert 'Your profile has been updated' in rv.data.decode("utf-8")
        assert current_user.username.lower() == 'jim'
        assert current_user.email == 'jim@example.com'
        assert current_user.check_password('foobar')
        assert current_user.about_me == 'test'

        # checking successful edit
        rv = self.edit(u, 'james', 'james@example.com', 'pharos1', 'something')
        assert 'Your profile has been updated' in rv.data.decode("utf-8")
        assert current_user.username.lower() == 'james'
        assert current_user.email == 'james@example.com'
        assert current_user.check_password('pharos1')
        assert current_user.about_me == 'something'


if __name__ == '__main__':
    unittest.main()
