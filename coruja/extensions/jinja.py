from flask import Flask
from wtforms import Field
from wtforms.validators import DataRequired


def is_field_required(field: Field):
    """Verifica se determinada field possui validador DataRequired

    Args:
        field (Field): Field

    Returns:
        bool: Se o field possui validador DataRequired
    """
    return any(isinstance(v, DataRequired) for v in field.validators)


def init_app(app: Flask):
    app.jinja_env.globals.update(is_field_required=is_field_required)
