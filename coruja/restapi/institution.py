from typing import Dict

from flask import Blueprint, Flask, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..decorators import proxy_access
from ..forms import InstitutionForm
from ..utils import database_manager, form_to_dict

bp = Blueprint("institution", __name__, url_prefix="/instituicao")


@bp.route("/criar", methods=["GET", "POST"])
@login_required
def get_post_institution_creation():
    """
    Rota para criar uma nova instituição.

    Esta rota é acessível através dos métodos GET e POST. Se o usuário
    atual não for autorizado a criar instituições, retorne um erro 403.
    """

    form = InstitutionForm()

    if request.method == "POST" and form.validate_on_submit():
        institution_data: Dict[str, str | bool] = form_to_dict(form)["data"]
        institution_administrators = institution_data.pop("admin_ids", [])
        institution_data.pop("csrf_token", None)
        institution_data.pop("submit", None)

        database_manager.add_institution(
            **institution_data,
            administrators=institution_administrators,
        )
        flash(
            f"Instituição {institution_data.get('name')!r} criada com sucesso",
            "success",
        )
        return redirect(url_for("institution.get_institution"))

    flash("Encontramos um erro ao tentar criar a instituição", "danger")
    return render_template("institution/create.html", form=form)


@bp.route("/<int:institution_id>", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="institution", kind_access="read")
def get_institution(institution_id: int):
    return "Em construção"


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
