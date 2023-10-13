from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = "auth.login"  # type: ignore


def init_app(app: Flask) -> None:
    login_manager.init_app(app)
