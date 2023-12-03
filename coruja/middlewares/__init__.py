from flask import Flask

from .middlewares import init_middleware_login


def init_middlewares(app: Flask) -> None:
    init_middleware_login(app)
