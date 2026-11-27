import os
from dotenv import load_dotenv
import redis
from datetime import timedelta
from pathlib import Path

load_dotenv()

class Config:
    STUDENT_DATA_PATH = os.getenv("STUDENT_DATA_PATH", "data/students.csv")
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "data/bminerva.db")
    NOTES_PATH = os.getenv("NOTES_PATH", "data/notes.txt")

    SESSION_DB_PATH = os.getenv("SESSION_DB_PATH", "data/sessions.db")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(Path(SESSION_DB_PATH).resolve()).replace("\\", "/")

    SECRET_KEY = os.getenv("SECRET_KEY")

    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY_TABLE = "sessions"
    SESSION_CLEANUP_N_REQUESTS = 100

    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(1)
    SESSION_USE_SIGNER = True

    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "1") == "1"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"