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

from ..decorators import proxy_access
from ..forms import OrganForm
from ..utils import database_manager, form_to_dict

bp = Blueprint("organ", __name__, url_prefix="/orgao")


@bp.route("/<int:organ_id>")
@login_required
@proxy_access(kind_object="organ", kind_access="read")
def get_organ(organ_id: int):
    """Rota para retornar a página de detalhes de um órgão.

    Args:
        organ_id (int): ID do orgão a ser visualizado.
    """
    organ = database_manager.get_organ(organ_id)
    institutions = database_manager.get_institutions(current_user.id)  # type: ignore

    return render_template(
        "organ/organ.html",
        organ=organ,
        institutions=institutions,
    )


@bp.route("/criar", methods=["GET", "POST"])
@login_required
# @proxy_access(kind_object="organ", kind_access="create")
# basicamente está comentado pois não foi implementado uma verificação via permissions da role (ainda)
def create_organ():
    """
    Rota para criar um novo órgão.

    Esta rota é acessível através dos métodos GET e POST. Se o usuário
    atual não for um administrador de órgãos, será retornado um erro 403.
    """
    if not database_manager.is_organ_administrator(current_user):
        abort(403)

    form = OrganForm()

    if request.method == "POST":
        if form.validate_on_submit():
            organ: Dict[str, str | bool] = form_to_dict(form)["data"]
            organ_administrators = organ.pop("admin_ids", [])
            organ.pop("csrf_token", None)
            organ.pop("submit", None)

            database_manager.add_organ(
                **organ,
                administrators=organ_administrators,
            )
            flash(f"Orgão {organ.get('name')} criado com sucesso", "success")
            return redirect(url_for("application.home"))

        flash("Encontramos um erro ao tentar criar o órgão", "danger")
    return render_template("organ/create.html", form=form)


@bp.route("/<int:organ_id>/editar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="organ", kind_access="update")
def edit_organ(organ_id: int):
    """Rota para edição de orgão específico pelo seu ID.

    Args:
        organ_id (int): ID do orgão a ser editado.
    """
    form = OrganForm()
    organ = database_manager.get_organ(organ_id)

    if form.validate_on_submit() and organ:
        form = form_to_dict(form)["data"]
        form.pop("csrf_token", None)
        form.pop("submit", None)

        if organ := database_manager.update_organ(organ, form):
            flash("Orgão atualizada com sucesso", "success")
            return redirect(url_for("organ.get_organ", organ_id=organ.id))

        flash("Ocorreu um erro ao atualizar o orgão", "danger")
    return render_template("organ/edit.html", form=form, organ=organ)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
