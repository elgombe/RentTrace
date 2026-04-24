from flask import Blueprint, request, session, jsonify, redirect, url_for
from app.controllers.auth_controller import login_user, logout_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or request.form
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    result = login_user(email, password)

    if result["success"]:
        session["user_id"] = result["user_id"]
        session["email"] = result["email"]
        session.permanent = True
        return jsonify({"success": True, "redirect": "/dashboard"})

    return jsonify({"success": False, "error": result["error"]}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    session.clear()
    return jsonify({"success": True, "redirect": "/login"})


@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 401
    return jsonify({"authenticated": True, "email": session.get("email")})