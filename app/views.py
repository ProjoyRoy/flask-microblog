from flask import render_template, flash, redirect, url_for, request, g
from app import app, db, lm
from .forms import LoginForm, SignupForm, EditForm
from .models import User
from flask.ext.login import login_user, logout_user,\
    current_user, login_required
from oauth import OAuthSignIn
from datetime import datetime


@lm.user_loader
def load_user(id):
    if User.query.get(id) is not None:
        return User.query.get(id)
    else:
        return None


@app.before_request
def before_rquest():
    g.user = current_user


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    # return to index page if already logged in
    if g.user is not None and g.user.is_authenticated:
        flash('Already logged in')
        return redirect(url_for('index'))
    # if not logged in
    form = LoginForm()
    if request.method == 'POST':
        if form.validate() == True:
            remember_me = False
            if 'remember_me' in request.form:
                remember_me = True
            email = str(form.email.data)
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(form.password.data):
                # db.session.add(user)
                # db.session.commit()
                print(remember_me)
                login_user(user, remember=remember_me)
                return redirect(url_for('profile'))
        else:  # form contains invalid data
            return render_template('login.html', form=form)
    elif request.method == 'GET':
        return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    if email is None:
        flash('Authentication failed. User account requires valid email.\
               Please sign up or log in with a different account')
        return redirect(url_for('index'))
    user = User.query.filter_by(email=email).first()
    if not user:
        if username is None or username == "":
            username = email.split('@')[0]
        this_username = User.pick_unique_name(username)
        user = User(social_id=social_id, name=this_username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('profile'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not g.user.is_anonymous:
        flash('Need to log out before signing up.')
        return redirect(url_for('index'))
    else:
        form = SignupForm()
        if request.method == 'POST':
            if form.validate() == False:
                return render_template('signup.html', form=form)
            else:
                newuser = User(form.name.data, form.email.data,
                               form.password.data)
                db.session.add(newuser)
                db.session.commit()
                login_user(newuser, True)
                return redirect(url_for('profile'))
        elif request.method == 'GET':
            return render_template('signup.html', form=form)


@app.route('/profile')
@login_required
def profile():
    return redirect(url_for('user', name=g.user.name))


@app.route('/user/<name>')
@login_required
def user(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        flash('User %s not found.' % name)
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.name = form.name.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('profile'))
    else:
        form.name.data = g.user.name
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)
