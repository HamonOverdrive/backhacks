# separate forms file to import

# pycharms way of using FLask-WTForm
from flask_wtf import Form
from wtforms import StringField, BooleanField, validators, PasswordField, TextAreaField


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# Comments Form Class
class CommentsForm(Form):
    comment = StringField('Comment', [validators.Length(min=0)])


# Article/Discussion Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])