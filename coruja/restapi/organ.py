from typing import Dict

from flask import Blueprint, Flask, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..decorators import institution_access, proxy_access
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

    def _access(institution):
        return institution_access(institution.id, current_user, "read")

    institutions = list(filter(_access, organ.institutions))  # type: ignore

    return render_template(
        "organ/organ.html",
        organ=organ,
        institutions=institutions,
    )


@bp.route("/criar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="organ", kind_access="create")
def create_organ():
    """
    Rota para criar um novo órgão.

    Esta rota é acessível através dos métodos GET e POST. Se o usuário
    atual não for um administrador de órgãos, será retornado um erro 403.
    """
    form = OrganForm()

    if request.method == "POST" and form.validate_on_submit():
        organ: Dict[str, str | bool] = form_to_dict(form)["data"]
        organ_administrators = organ.pop("admin_ids", [])
        organ.pop("csrf_token", None)
        organ.pop("submit", None)

        database_manager.add_organ(
            **organ,
            administrators=organ_administrators,
        )
        flash(f"Orgão {organ.get('name')} criado", "success")
        return redirect(url_for("application.home"))

    return render_template("organ/create.html", form=form)


@bp.route("/<int:organ_id>/editar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="organ", kind_access="update")
def edit_organ(organ_id: int):
    """Rota para edição de orgão específico pelo seu ID.

    Args:
        organ_id (int): ID do orgão a ser editado.
    """
    organ = database_manager.get_organ(organ_id)
    form = OrganForm(obj=organ, is_edit=True)

    if form.validate_on_submit() and organ:
        form = form_to_dict(form)["data"]
        form.pop("csrf_token", None)
        form.pop("submit", None)

        if organ := database_manager.update_organ(organ, form):
            flash(f"Orgão {organ.name} atualizado", "success")
            return redirect(url_for("organ.get_organ", organ_id=organ.id))

    return render_template("organ/edit.html", form=form, organ=organ)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
