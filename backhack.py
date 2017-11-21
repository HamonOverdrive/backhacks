from flask import Flask, render_template, flash, request, url_for, redirect, session, logging

# not sure if i need below
# from flask_mysqldb import MySQL

from passlib.hash import sha256_crypt
from functools import wraps
from forms import RegisterForm, CommentsForm, ArticleForm

# import mysql connection with this
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

# adding this below made flash work why?
app.secret_key = "clave secreta"


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

# Single discussion page
@app.route('/discussion/<string:id>/', methods=['GET', 'POST'])
def discussion_page(id):
    #POSSIBLE BUG HERE
    form = CommentsForm(request.form)
    # Create cursor
    c, conn = connection()

    # Get articles with corresponding comments by using JOIN
    result = c.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = c.fetchone()

    # Close connection
    c.close()
    conn.close()

    # article title is need so you can put inside comment table
    current_title = article['title']

    if request.method == 'POST' and form.validate():
        # get form body data as this is post method and create cursor dont need if post as this is post already at the top
        # THIS IS RETURNING AN EMPTY STRING WHY
        new_comment = form.comment.data

        # Create Cursor
        c, conn = connection()

        # Execute query
        c.execute("INSERT INTO comments(article_title, comment, author) VALUES(%s, %s, %s)",
                  (current_title, new_comment, session['username']))

        # Commit to DB
        conn.commit()

        # Close connection
        c.close()
        conn.close()

        flash('Comment added!', 'success')
        return redirect(url_for('dashboard'))

    # GET HISTORY

    return render_template('discussion.html', article=article, form=form)

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

# if logged in redirects here and is DASHBOARD
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
    # Close connection
    c.close()
    conn.close()

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

# Edit Article/Discussion remember differs based on user
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create Cursor
    c, conn = connection()

    # Get article by id
    result = c.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = c.fetchone()
    c.close()
    conn.close()

    # Get form
    form = ArticleForm(request.form)

    # Populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']

    # get author so you can verify only current author can edit post. Remember to include how solved in readme
    current_author = article['author']
    if session['username'] == current_author:
        flash('Article author matches current user you may edit', 'success')
    else:
        flash('Cannot edit must be appropriate author', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create Cursor
        c, conn = connection()

        # Execute
        c.execute("UPDATE articles SET title=%s, body=%s WHERE id = %s", (title, body, id))

        # Commit to DB
        conn.commit()

        # Close connection
        c.close()
        conn.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)

# Delete Article/discussion different based on user
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create Cursor for article
    c, conn = connection()

    # Get article by id
    result = c.execute("SELECT * FROM articles WHERE id = %s", [id])

    # represents an object in the articles table
    article = c.fetchone()

    # compared currented logged in user to article author to check if you can delete
    current_author = article['author']
    if session['username'] == current_author:
        pass
    else:
        flash('Cannot delete must be appropriate author', 'danger')
        return redirect(url_for('dashboard'))
    # ends here

    # Execute second delete query
    c.execute("DELETE FROM articles WHERE id=%s", [id])

    # Commit to DB
    conn.commit()

    # Close connection
    c.close()
    conn.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))

# #adding COMMENTS NOT WORKING AS THE COMMENT MATERIAL NOT GOING INSIDE SQL TABLE
# @app.route('/add_comments/<string:id>/', methods=['POST'])
# @is_logged_in
# def add_comments(id):
#     form = CommentsForm(request.form)
#     # Create cursor TO GET ARTICLE TITLE TO JOIN LATER
#     c, conn = connection()
#     # Get article by id
#     c.execute("SELECT * FROM articles WHERE id = %s", [id])
#     # represents an object in the articles table
#     article = c.fetchone()
#     # close cursors
#     c.close()
#     conn.close()
#     # article title is need so you can put inside comment table
#     current_title = article['title']
#
#     # possible bug HERE
#     # get form body data as this is post method and create cursor dont need if post as this is post already at the top
#     new_comment = form.comment.data
#
#     # Create Cursor
#     c, conn = connection()
#
#     # Execute query
#     c.execute("INSERT INTO comments(article_title, comment, author) VALUES(%s, %s, %s)", (current_title, new_comment, session['username']))
#
#     # Commit to DB
#     conn.commit()
#
#     # Close connection
#     c.close()
#     conn.close()
#
#     flash('Comment added!', 'success')
#
#     return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run()
