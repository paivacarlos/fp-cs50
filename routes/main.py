from flask import Blueprint, render_template, redirect, session, abort
from utils.security import login_required
from services.db import get_db

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

@main_bp.route("/conference/<int:conference_id>/newspaper", methods=["GET"])
@login_required
def newspaper(conference_id):
    user_id = session["user_id"]
    with get_db() as conn:
        conference = conn.execute(
            "SELECT * FROM conferences WHERE id = ? AND user_id = ?",
            (conference_id, user_id)
        ).fetchone()
        
    if not conference:
        abort(404)
        
    return render_template("newspaper.html", conference=conference)
