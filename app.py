import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from routes.auth import auth_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "key-secret-develop-env")

app.register_blueprint(auth_bp)
