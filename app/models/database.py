import os
from dotenv import load_dotenv

load_dotenv()

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_default_user()


def seed_default_user():
    from app.models.user_model import User
    import bcrypt

    DEFAULT_EMAIL = os.environ.get("DEFAULT_EMAIL")
    DEFAULT_PASSWORD = os.environ.get("DEFAULT_PASSWORD")

    existing = User.query.filter_by(email=DEFAULT_EMAIL).first()

    if existing is None:
        password_hash = bcrypt.hashpw(
            DEFAULT_PASSWORD.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        ).decode("utf-8")

        user = User(email=DEFAULT_EMAIL, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()