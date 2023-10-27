from flask import Flask
from wtforms import Field
from wtforms.validators import DataRequired

from ..decorators import proxy_access_function


def is_field_required(field: Field):
    """Verifica se determinada field possui validador DataRequired

    Args:
        field (Field): Field

    Returns:
        bool: Se o field possui validador DataRequired
    """
    return any(isinstance(v, DataRequired) for v in field.validators)


def init_app(app: Flask):
    app.jinja_env.globals.update(
        is_field_required=is_field_required, proxy_access=proxy_access_function
    )
