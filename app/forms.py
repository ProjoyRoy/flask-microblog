from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField,\
                    TextAreaField
from wtforms.validators import DataRequired, Length
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
    name = StringField('name', validators=[DataRequired()])
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
            self.email.errors.append("That email is already taken")
            return False
        else:
            return True


class EditForm(Form):
    name = StringField('name')
    email = StringField('email')
    password = PasswordField('password', validaotors=[Length(min=6, max=30)])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
