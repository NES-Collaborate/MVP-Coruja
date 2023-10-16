from flask import Flask

from flask_session import Session

session = Session()


def init_app(app: Flask) -> None:
    session.init_app(app)
