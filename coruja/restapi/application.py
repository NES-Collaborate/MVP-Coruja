from flask import Blueprint, Flask, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..forms import OrganForm
from ..utils import database_manager

bp = Blueprint("application", __name__, url_prefix="/app")


@bp.route("/home")
@login_required
def home():
    form = OrganForm()
    orgaos = database_manager.get_organs_by_user_id(current_user.id)  # type: ignore

    return render_template("application/home.html", orgaos=orgaos, form=form)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
