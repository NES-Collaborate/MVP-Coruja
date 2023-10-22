from typing import Dict

from flask import (
    Blueprint,
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from coruja.extensions import database

from ..decorators import proxy_access
from ..utils import database_manager, form_to_dict

bp = Blueprint("unit", __name__, url_prefix="/unidade")


@bp.route("/<int:unit_id>")
@login_required
@proxy_access(kind_object="unit", kind_access="read")
def get_unit(unit_id: int):
    unit = database_manager.get_unit(unit_id)
    analysis = database_manager.get_analysis(current_user.id)  # type: ignore

    return render_template("unit/unit.html", unit=unit, analysis=analysis)


@bp.route("/criar", methods=["GET", "POST"])
@login_required
def create_unit():
    return ""


@bp.route("/<int:unit_id>/editar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="unit", kind_access="update")
def edit_unit(unit_id: int):
    return ""


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
