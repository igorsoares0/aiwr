from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Enter your email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Enter your password'})
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)], render_kw={'placeholder': 'First name'})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)], render_kw={'placeholder': 'Last name'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Enter your email'})
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'placeholder': 'Create a password'})
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm your password'})
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or try logging in.')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Enter your email'})
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'placeholder': 'Enter new password'})
    password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm new password'})
    submit = SubmitField('Reset Password')