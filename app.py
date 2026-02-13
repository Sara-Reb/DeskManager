import os

from flask import Flask, flash, render_template, request, redirect, session
from flask_session import Session
from redis import Redis
from helpers import login_required



app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
    return render_template('/index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == 'GET':
        return render_template('/login.html')