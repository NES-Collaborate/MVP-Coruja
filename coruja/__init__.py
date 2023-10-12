from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager
from importlib import import_module
from dotenv import dotenv_values


dotenv = dotenv_values(".env")


settings = {
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "SESSION_TYPE": "filesystem",
    "SESSION_PERMANENT": False,
    "PERMANENT_SESSION_LIFETIME": 60 * 60 * 24,
    "CSRF_ENABLED": True,
    "CSRF_SESSION_TIMEOUT": 60 * 60 * 24,
}

settings.update(dotenv.copy())


app = Flask(__name__)
app.config.from_mapping(settings)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

session = Session(app)
csrf = CSRFProtect(app)
cors = CORS(app)
db = SQLAlchemy(app)


modules = ["api", "auth", "database", "models", "application", "forms"]
for module in modules:
    bp = getattr(import_module(f"coruja.{module}"), "bp", None)
    if bp is not None:
        app.register_blueprint(bp)
