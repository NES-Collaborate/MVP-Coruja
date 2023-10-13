from flask import Flask

from .extensions import configurations
from .restapi import api, application


def create_app() -> Flask:
    app = Flask(__name__)
    configurations.init_app(app)
    configurations.load_extensions(app)

    api.init_api(app)
    application.init_api(app)

    return app
