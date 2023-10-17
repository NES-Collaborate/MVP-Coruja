from flask import Flask

from .analysis import init_api as init_analysis
from .api import init_api
from .application import init_api as init_aplication
from .auth import init_api as init_auth
from .organ import init_api as init_organ


def init_apis(app: Flask) -> None:
    init_api(app)
    init_auth(app)
    init_aplication(app)
    init_organ(app)
    init_analysis(app)
