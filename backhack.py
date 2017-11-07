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

# # Config MySQL other example on main py file
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '123456'
# app.config['MYSQL_DB'] = 'myflaskapp'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# # init MYSQL
# mysql = MySQL(app)

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
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        c, conn = connection()

        # Execute query
        c.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
                    (name, email, username, password))

        # Commit to DB
        conn.commit()

        # Close connection
        c.close()
        conn.close()

        # after comma is the category for the flash so you can change type of flash based on that
        flash('You are now registered and can log in', 'success')

        # if using redirect have to use url_for()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# User Login
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        c, conn = connection()

        # Get user by username
        result = c.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = c.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                app.logger.info('PASSWORD MATCHED')
            else:
                app.logger.info('PASSWORD NOT MATCHED')
        else:
            app.logger.info('NO USER')

    return render_template('login.html')



if __name__ == '__main__':
    app.run()
