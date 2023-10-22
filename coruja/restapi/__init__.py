from flask import Flask

from .admin import init_api as init_admin
from .analysis import init_api as init_analysis
from .api import init_api
from .application import init_api as init_aplication
from .auth import init_api as init_auth
from .institution import init_api as init_institution
from .organ import init_api as init_organ
from .unit import init_api as init_unit
from .analysis_risk import init_api as init_analysis_risk


def init_apis(app: Flask) -> None:
    init_api(app)
    init_auth(app)
    init_aplication(app)
    init_organ(app)
    init_analysis(app)
    init_admin(app)
    init_institution(app)
    init_unit(app)
    init_analysis_risk(app)
