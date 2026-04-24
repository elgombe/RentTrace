import bcrypt
from app.models.user_model import User
from app.models.database import db


def login_user(email: str, password: str) -> dict:
    if not email or not password:
        return {"success": False, "error": "Email and password are required"}

    user = User.query.filter_by(email=email.lower()).first()

    if user is None:
        return {"success": False, "error": "Invalid email or password"}

    password_matches = bcrypt.checkpw(
        password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    )

    if not password_matches:
        return {"success": False, "error": "Invalid email or password"}

    return {"success": True, "user_id": user.id, "email": user.email}


def logout_user():
    pass  # Session cleared in the route


def hash_password(password: str) -> str:
    from flask import current_app
    rounds = current_app.config.get("BCRYPT_ROUNDS", 12)
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=rounds),
    ).decode("utf-8")


def register_user(email: str, password: str) -> dict:
    if not email or not password:
        return {"success": False, "error": "Email and password are required"}

    existing = User.query.filter_by(email=email.lower()).first()
    if existing:
        return {"success": False, "error": "Email already registered"}

    password_hash = hash_password(password)
    user = User(email=email.lower(), password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return {"success": True, "user_id": user.id}