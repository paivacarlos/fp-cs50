from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
from flask import session, redirect, url_for, flash

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def check_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You need to be logged in to access this page.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated
