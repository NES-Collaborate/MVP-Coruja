from flask import Flask

from .admin import bp as admin_bp
from .category import bp as category_bp
from .logs import bp as logs_bp


def init_api(app: Flask):
    admin_bp.register_blueprint(logs_bp)
    admin_bp.register_blueprint(category_bp)
    app.register_blueprint(admin_bp)
