from typing import Dict

from flask import Blueprint, Flask, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..decorators import proxy_access
from ..forms import InstitutionForm
from ..utils import database_manager, form_to_dict

bp = Blueprint("institution", __name__, url_prefix="/instituicao")


@bp.route("/criar", methods=["GET", "POST"])
@login_required
def create_institution():
    """
    Rota para criar uma nova instituição.

    Esta rota é acessível através dos métodos GET e POST. Se o usuário
    atual não for autorizado a criar instituições, retorne um erro 403.
    """
    # Inicialização do formulário
    form = InstitutionForm()

    # Verifica se o método é POST e o formulário é válido
    if request.method == "POST" and form.validate_on_submit():
        # Coleta os dados do formulário e remove campos indesejados
        institution_data = form_to_dict(form)["data"]
        administrators = institution_data.pop("admin_ids", [])
        for field in ["csrf_token", "submit"]:
            institution_data.pop(field, None)

        institution = database_manager.add_institution(
            **institution_data,
            administrators=administrators,
        )

        flash(
            f"Instituição {institution_data.get('name')!r} criada com sucesso",
            "success",
        )
        return redirect(
            url_for(
                "institution.get_institution", institution_id=institution.id
            )
        )

    if request.method == "GET":
        return render_template("institution/create.html", form=form)

    flash("Encontramos um erro ao tentar criar a instituição", "danger")
    return render_template("institution/create.html", form=form)


@bp.route("/<int:institution_id>")
@login_required
@proxy_access(kind_object="institution", kind_access="read")
def get_institution(institution_id: int):
    """Rota para retornar a página de detalhes de uma instituição.

    Args:
        institution_id (int): ID da instituição a ser visualizada.
    """

    institution = database_manager.get_institution(institution_id)
    # units = database_manager.get_units(current_user.id)
    units = None

    return render_template(
        "institution/institution.html", institution=institution, units=units
    )


@bp.route("/<int:institution_id>/editar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="institution", kind_access="update")
def edit_institution(institution_id: int):
    """Rota para edição de uma instituição específica pelo seu ID.

    Args:
        insitution_id (int): ID da instituição a ser editada.
    """

    institution = database_manager.get_institution(institution_id)
    form = InstitutionForm(obj=institution)

    # TODO: Checagem do submit do form

    return render_template(
        "institution/edit.html", form=form, institution=institution
    )


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
