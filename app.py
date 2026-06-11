import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from routes.auth import auth_bp
from routes.main import main_bp
from routes.api import api_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False # Alterar para TRUE quando subir me PROD
)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "key-secret-develop-env")

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)
