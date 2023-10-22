from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def init_app(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
