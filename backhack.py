from flask import Flask, render_template, flash, request, url_for, redirect, session

#pycharms way of using FLask-WTForm
from flask_wtf import Form
from wtforms import StringField, BooleanField, validators, PasswordField
from passlib.hash import sha256_crypt


from functools import wraps

app = Flask(__name__)

#adding this below made flash work why?
app.secret_key="clave secreta"

@app.route('/')
def homepage():
    return render_template("main.html")

@app.route('/mission/')
def missionpage():
    return render_template("mission.html")

@app.route('/login/')
def login_page():
    return render_template("login.html")



if __name__ == '__main__':
    app.run()
