from flask import Flask

from .middlewares import init_middlware_login


def init_middlewares(app: Flask) -> None:
    init_middlware_login(app)
