from flask import Flask
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
cors = CORS()


def init_app(app: Flask) -> None:
    csrf.init_app(app)
    cors.init_app(app)
