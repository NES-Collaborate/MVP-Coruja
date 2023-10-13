from flask import Flask

from .api import init_api
from .application import init_api as init_aplication
from .auth import init_api as init_auth


def init_apis(app: Flask) -> None:
    init_api(app)
    init_auth(app)
    init_aplication(app)
