from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class SignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    skills = StringField('Skills', validators=[Length(max=200)])
    avatar_url = StringField('Avatar URL', validators=[Length(max=200)])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[Length(max=200)])

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    skills = StringField('Skills', validators=[Length(max=200)])
    avatar_url = StringField('Avatar URL', validators=[Length(max=200)])

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
