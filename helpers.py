from functools import wraps
from flask import redirect, session, render_template
import sqlite3
import datetime as dt

def login_required(f):

    # Decorator to check if the user is logged in before accessing a route
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/landing')
        return f(*args, **kwargs)
    return decorated_function
    

def get_db_connection():
    # Function to establish a connection to the SQLite database
    connection = sqlite3.connect('deskflow.db')
    connection.row_factory = sqlite3.Row
    return connection

def display_date(date_str):
    # Function to convert a date string into a more readable format
    if not date_str:
        return None
    date = dt.datetime.fromisoformat(date_str)
    today = dt.date.today()
    delta = (date.date() - today).days
    if delta == 0:
        return 'Oggi'
    elif delta == -1:
        return 'Ieri'
    elif delta == 1:
        return 'Domani'
    else:
        if date.hour == 0 and date.minute == 0 and date.second == 0:
            return date.strftime('%d %b %Y')
        else:
            return date.strftime('%d %b %Y %H:%M')
    