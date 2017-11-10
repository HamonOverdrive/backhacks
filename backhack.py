from flask import Flask, render_template, flash, request, url_for, redirect, session, logging

# not sure if i need below
# from flask_mysqldb import MySQL

#pycharms way of using FLask-WTForm
from flask_wtf import Form
from wtforms import StringField, BooleanField, validators, PasswordField, TextAreaField
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

@app.route('/discussions/')
def discussions_page():
    # Create cursor
    c, conn = connection()

    # Get articles
    result = c.execute("SELECT * FROM articles")

    articles = c.fetchall()
    if result > 0:
        return render_template('discussions.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('discussions.html', msg=msg)
    # Close connection
    c.close()
    conn.close()

# Single discussion link
@app.route('/discussion/article/<string:id>/')
def discussion_page(id):
    # Create cursor
    c, conn = connection()

    # Get articles
    result = c.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = c.fetchone()

    return render_template('discussion.html', article=article)


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
    form = RegisterForm(request.form)
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
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error, form=form)
            # Close connection
            c.close()
            conn.close()

        else:
            error = 'Username not found'
            return render_template('login.html', error=error, form=form)

    return render_template('login.html', form=form)

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout/')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#if logged in redirects here and is DASHBOARD
@app.route('/dashboard/')
@is_logged_in
def dashboard():
    # Create cursor
    c, conn = connection()

    # Get articles
    result = c.execute("SELECT * FROM articles")

    articles = c.fetchall()
    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    #Close connection
    c.close()
    conn.close()

# Article/Discussion Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Add Article/Discussion
@app.route('/add_article/', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create Cursor
        c, conn = connection()

        # Execute
        c.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

        # Commit to DB
        conn.commit()

        # Close connection
        c.close()
        conn.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)



if __name__ == '__main__':
    app.run()
