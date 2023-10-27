from flask import Blueprint, Flask, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from coruja.decorators.proxy import analysis_access
from coruja.forms import UnitForm

from ..decorators import proxy_access
from ..utils import database_manager, form_to_dict

bp = Blueprint("unit", __name__, url_prefix="/unidade")


@bp.route("/<int:unit_id>")
@login_required
@proxy_access(kind_object="unit", kind_access="read")
def get_unit(unit_id: int):
    unit = database_manager.get_unit(unit_id)

    analyses = [analysis for analysis in unit.analyses if analysis_access(analysis.id, current_user, "read")]  # type: ignore

    return render_template("unit/unit.html", unit=unit, analyses=analyses)


@bp.route("/criar", methods=["GET", "POST"])
@login_required
def create_unit():
    form = UnitForm()

    parent_id = request.args.get("parent_id", default=None, type=int)
    if not parent_id:
        flash("Instituição não especificada", "danger")
        return redirect(url_for("application.home"))

    @proxy_access(kind_object="institution", kind_access="update")
    def get_institution(*, institution_id: int):
        return database_manager.get_institution(institution_id)

    institution = get_institution(institution_id=parent_id)

    if request.method == "POST" and form.validate_on_submit():
        unit_data = form_to_dict(form)["data"]
        administrators = unit_data.pop("admin_ids", [])
        for field in ["csrf_token", "submit"]:
            unit_data.pop(field, None)

        unit = database_manager.add_unit(
            **unit_data, administrators=administrators
        )

        institution.add_unit(unit)  # type: ignore

        flash(
            f"Unidade {unit_data.get('name')!r} criada com sucesso",
            "success",
        )
        return redirect(url_for("unit.get_unit", unit_id=unit.id))

    return render_template("unit/create.html", form=form)


@bp.route("/<int:unit_id>/editar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="unit", kind_access="update")
def edit_unit(unit_id: int):
    unit = database_manager.get_unit(unit_id)
    form = UnitForm(obj=unit)

    if form.validate_on_submit() and unit:
        form = form_to_dict(form)["data"]
        form.pop("csrf_token", None)
        form.pop("submit", None)

        if unit := database_manager.update_unit(unit, form):
            flash("Unidade atualizada com sucesso", "success")
            return redirect(
                url_for(
                    "unit.get_unit",
                    unit_id=unit.id,
                )
            )

    return render_template("unit/edit.html", form=form, unit=unit)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
