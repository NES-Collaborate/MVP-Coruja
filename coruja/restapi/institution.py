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

from ..forms import InstitutionForm
from ..utils import database_manager, form_to_dict

institution_bp = Blueprint("institution", __name__, url_prefix="/instituicao")


@institution_bp.route("/criar", methods=["GET", "POST"])
@login_required
def get_post_institution_creation():
    """
    Rota para criar uma nova instituição.

    Esta rota é acessível através dos métodos GET e POST. Se o usuário
    atual não for autorizado a criar instituições, retorne um erro 403.
    """
    if not current_user.is_authorized_to_create_institution():
        abort(403)

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
        return redirect(url_for("application.home"))

    flash("Encontramos um erro ao tentar criar a instituição", "danger")
    return render_template("institution/create.html", form=form)


def init_api(app: Flask) -> None:
    app.register_blueprint(institution_bp)
