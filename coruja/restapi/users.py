from flask import Blueprint, Flask

bp = Blueprint("users", __name__, url_prefix="/users")


def init_app(app: Flask) -> None:
    app.register_blueprint(bp)
