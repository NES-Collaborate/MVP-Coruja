from importlib import import_module

from dynaconf import FlaskDynaconf
from flask import Flask

# from . import auth, database, securancy, sessions


def load_extensions(app: Flask) -> None:
    for extension in app.config.EXTENSIONS:  # type: ignore
        # Split data in form `extension.path:factory_function`
        module_name, factory = extension.split(":")

        # Dynamically import extension module.
        ext = import_module(module_name)

        # Invoke factory passing app.
        getattr(ext, factory)(app)


def init_app(app: Flask) -> None:
    FlaskDynaconf(app)
