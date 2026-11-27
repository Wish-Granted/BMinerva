from flask import Flask
from pathlib import Path

from .config import Config
from .students.csv_repository import CSVStudentRepository
from .students.routes import students_bp
from .lists.sqlite_list_repository import SQLiteListRepository
from .lists.routes import lists_bp
from .selections.sqlite_selection_repository import SQLiteSelectionRepository
from .selections.routes import selection_bp
from .notes.txt_notes import TXTNotes
from .notes.routes import notes_bp
from .auth.handoff_store import HandoffStore
from .auth.routes import auth_bp, web_auth_bp
from .eminerva.routes import eminerva_bp
from .main.routes import main_bp
from .extensions import session_ext, db

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)

    Path(app.config["SESSION_DB_PATH"]).parent.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    app.config["SESSION_SQLALCHEMY"] = db
    session_ext.init_app(app)
    
    app.handoff_store = HandoffStore(app.config["SESSION_DB_PATH"])
    app.student_repository = CSVStudentRepository(app.config["STUDENT_DATA_PATH"]) #change when using LDAP
    app.list_repository = SQLiteListRepository(app.config["SQLITE_DB_PATH"])
    app.selection_repository = SQLiteSelectionRepository(app.config["SQLITE_DB_PATH"])
    app.notes = TXTNotes(app.config["NOTES_PATH"])
    
    app.register_blueprint(students_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(web_auth_bp)
    app.register_blueprint(eminerva_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(lists_bp)
    app.register_blueprint(selection_bp)
    app.register_blueprint(notes_bp)

    return app