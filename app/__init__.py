from flask import Flask
from config import Config
from app.models.database import init_db


def create_app():
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(Config)

    # ── Import all models so SQLAlchemy can create their tables ──
    import app.models  # noqa: F401

    # ── Initialise database ───────────────────────────────────
    init_db(app)

    # ── Register blueprints ───────────────────────────────────
    from app.api.auth import auth_bp
    from app.api.tenants import tenants_bp
    from app.api.transactions import transactions_bp
    from app.api.receipts import receipts_bp
    from app.api.reconcile import reconcile_bp
    from app.api.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tenants_bp, url_prefix="/api/tenants")
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
    app.register_blueprint(receipts_bp, url_prefix="/api/receipts")
    app.register_blueprint(reconcile_bp, url_prefix="/api/reconcile")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    # ── Register view routes ──────────────────────────────────
    from app.api.views import views_bp

    app.register_blueprint(views_bp)

    return app