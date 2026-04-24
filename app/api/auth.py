from flask import Blueprint, request, jsonify, session, render_template

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    return render_template("login.html")