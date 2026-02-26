from functools import wraps
from flask import redirect, session, render_template
import sqlite3

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