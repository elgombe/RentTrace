from flask import Blueprint, render_template, redirect, url_for, session
from app.middleware.auth_guard import login_required

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
@login_required
def index():
    return redirect(url_for("views.dashboard"))


@views_bp.route("/login")
def login():
    if "user_id" in session:
        return redirect(url_for("views.dashboard"))
    return render_template("login.html")

@views_bp.route("/dashboard")
@login_required
def dashboard():
    return 'Dashboard Page - not implemented yet'


@views_bp.route("/tenants")
@login_required
def tenants():
    return 'Tenants Page - not implemented yet'


@views_bp.route("/upload")
@login_required
def upload():
    return 'Upload Page - not implemented yet'


@views_bp.route("/reconcile")
@login_required
def reconcile():
    return 'Reconcile Page - not implemented yet'