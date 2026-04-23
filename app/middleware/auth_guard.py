from functools import wraps
from flask import session, redirect, url_for, request, jsonify


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            # API requests get a 401, page requests get a redirect
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorised"}), 401
            return redirect(url_for("views.login"))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    """Returns the logged-in User object or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    from app.models.user_model import User
    return User.query.get(user_id)