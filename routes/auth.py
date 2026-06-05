from flask import Blueprint, render_template, request, session, flash, redirect
from services.db import query_db, execute_db
from utils.security import hash_password

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username_from_form = request.form.get("username")
        password_from_form = request.form.get("password")
        confirm_password_from_form = request.form.get("confirm_password")

        if not username_from_form or not password_from_form or not confirm_password_from_form:
            flash("Please, send all data.")
            return render_template("register.html")

        if password_from_form != confirm_password_from_form:
            flash("Passwords do not match.")
            return render_template("register.html")
        
        user = query_db("SELECT * FROM users WHERE username = ?", (username_from_form,), one=True)
        if user:
            flash("User already exists.")
            return render_template("register.html")
        
        password_hashed = hash_password(password_from_form)
        execute_db("INSERT INTO users (username, hash) VALUES (?, ?)", (username_from_form, password_hashed))

        flash("User created successfully.")

        user = query_db("SELECT * FROM users WHERE username = ?", (username_from_form,), one=True)
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect("/setup")
    return render_template("register.html")