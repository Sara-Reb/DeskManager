import requests

from flask import redirect, render_template, session
from functools import wraps

def login_required(f):

    # Decorator to check if the user is logged in before accessing a route
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function
    