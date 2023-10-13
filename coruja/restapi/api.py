from flask import Blueprint, Flask

bp = Blueprint("api", __name__, url_prefix="/api/v1")


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
