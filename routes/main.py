from flask import Blueprint, render_template, redirect, session
from utils.security import login_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["GET"])
def index():
    # Se o ID do usuário estiver na sessão, ele está logado
    if "user_id" in session:
        return redirect("/setup")
    # Caso contrário, redireciona para a tela de login
    return redirect("/login")

@main_bp.route("/setup", methods=["GET"])
@login_required
def setup():
    return render_template("setup.html")
