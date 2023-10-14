from flask import Flask

from .extensions import configurations


def create_app() -> Flask:
    app = Flask(__name__)
    configurations.init_app(app)
    configurations.load_extensions(app)

    return app
