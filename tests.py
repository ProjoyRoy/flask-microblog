#!/home/pj/.conda/envs/flask-microblog/bin/python
import os
import unittest

from unittest import TestCase
from datetime import datetime, timedelta
from flask import url_for
from config import basedir
from app import app, db
from app.models import User, Post
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
        assert username != 'neo'  # test that user was created in db

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = grav_url
        assert avatar[0:len(expected)] == expected

    def test_login_and_logout(self):
        u = User(username='john', email='john@example.com', password='foobar')
        self.create_user(u)
        assert u in db.session
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
        assert current_user.username.lower() == 'jim'
        assert current_user.email == 'jim@example.com'
        assert current_user.check_password('foobar')
        assert current_user.about_me == 'test'

        # checking successful edit
        rv = self.edit(u, 'james', 'james@example.com', 'pharos1', 'something')
        assert current_user.username.lower() == 'james'
        assert current_user.email == 'james@example.com'
        assert current_user.check_password('pharos1')
        assert current_user.about_me == 'something'

    def test_follow(self):
        u1 = User(username='dog', email='dog@god.com')
        u2 = User(username='cat', email='cat@feedme.com')
        self.create_user(u1)
        self.create_user(u2)
        # test that user 1 is not already following user 2
        assert u1.unfollow(u2) is None
        u = u1.follow(u2)  # make u1 follow u2 and store the returned user in u
        self.create_user(u)
        assert u1.follow(u2) is None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().username.lower() == 'cat'
        assert u2.followers.count() == 1
        assert u2.followers.first().username.lower() == 'dog'
        u = u1.unfollow(u2)
        assert u is not None
        self.create_user(u)
        assert not u1.is_following(u2)
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_follow_posts(self):
        # make four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        # make four posts
        utcnow = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  timestamp=utcnow + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  timestamp=utcnow + timedelta(seconds=2))
        p3 = Post(body="post from mary", author=u3,
                  timestamp=utcnow + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  timestamp=utcnow + timedelta(seconds=4))
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        # setup the followers
        u1.follow(u1)  # john follows himself
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u2)  # susan follows herself
        u2.follow(u3)  # susan follows mary
        u3.follow(u3)  # mary follows herself
        u3.follow(u4)  # mary follows david
        u4.follow(u4)  # david follows himself
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1 == [p4, p2, p1]
        assert f2 == [p3, p2]
        assert f3 == [p4, p3]
        assert f4 == [p4]

if __name__ == '__main__':
    unittest.main()
