from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField, \
    TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from .models import User


class LoginForm(Form):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(),
                                                     Length(min=6, max=30)])
    remember_me = BooleanField('remember_me', default=False)
    submit = SubmitField('Sign In')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user is None:
            self.email.errors.append("No such email")
            return False
        if not user.check_password(self.password.data):
            self.password.errors.append('Incorrect password')
            return False
        else:
            return True


class SignupForm(Form):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(),
                                                     Length(min=6, max=30)])
    submit = SubmitField('Create Account')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user:
            self.email.errors.append("There is already an account with \
                                          this email.")
            return False
        return True


class EditForm(Form):
    username = StringField('username', validators=[Optional()])
    email = StringField('email', validators=[Optional()])
    password = PasswordField('password', validators=[Optional(),
                                                     Length(min=6, max=30)])
    about_me = TextAreaField('about_me', validators=[Optional(),
                                                     Length(min=0, max=140)])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        user_name = User.query.filter_by(username=self.username.data).first()
        if user_name:
            self.username.errors.append('This username is already in use.\
                                        Please choose another one.')
            return False
        user_email = User.query.filter_by(email=self.email.data).first()
        if user_email:
            self.email.errors.append('This email is already in use.\
                                        Please choose another one.')
            return False
        return True


class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])
