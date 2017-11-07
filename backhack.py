from flask import Flask, render_template, flash, request, url_for, redirect, session, logging

# not sure if i need below
# from flask_mysqldb import MySQL

#pycharms way of using FLask-WTForm
from flask_wtf import Form
from wtforms import StringField, BooleanField, validators, PasswordField
from passlib.hash import sha256_crypt
from functools import wraps

#import mysql connection with this
from dbconnect import connection

app = Flask(__name__)

#adding this below made flash work why?
app.secret_key="clave secreta"

@app.route('/')
def homepage():
    return render_template("main.html")

@app.route('/mission/')
def missionpage():
    return render_template("mission.html")

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

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('register.html')
    return render_template('register.html', form=form)



if __name__ == '__main__':
    app.run()
