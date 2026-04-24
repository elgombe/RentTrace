import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "app")
DB_DIR   = os.path.join(DATA_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "data/uploads")

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


class Config:
    # ── Security ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # ── Database ──────────────────────────────────────────────
    DATABASE_PATH = os.path.join(DB_DIR, "renttrace.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DB_DIR, 'renttrace.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── File uploads ──────────────────────────────────────────
    UPLOAD_FOLDER = UPLOAD_DIR
    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "pdf", "png", "jpg", "jpeg"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ── Bcrypt ────────────────────────────────────�