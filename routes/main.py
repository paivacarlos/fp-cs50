from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/setup", methods=["GET"])
def setup():
    return render_template("setup.html")
