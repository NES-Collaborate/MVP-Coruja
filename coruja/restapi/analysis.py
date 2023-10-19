from flask import Blueprint, Flask, flash, redirect, render_template, url_for
from flask_login import login_required

from ..decorators import proxy_access
from ..forms import AnalysisForm
from ..utils import database_manager

bp = Blueprint("analysis", __name__, url_prefix="/analise")


@bp.route("/<int:analysis_id>")
@login_required
@proxy_access(kind_object="analysis", kind_access="read")
def get_analysis(analysis_id: int):
    analysis = database_manager.get_analysis(analysis_id)
    # TODO: Criar métodos para retornar uma lista de experts com seus respectivos
    # "progressos" dentro de uma determinada análise (notasDadas/notasPossíveis)
    experts = analysis.experts  # type: ignore [analysis isn't None]
    actives = database_manager.get_actives_by_analysis(analysis)  # type: ignore [analysis isn't None]
    context = {"analysis": analysis, "experts": experts, "actives": actives}
    return render_template("analysis/analysis.html", **context)


@bp.route("/<int:analysis_id>/editar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="analysis", kind_access="update")
def edit_analysis(analysis_id: int):
    form = AnalysisForm()
    analysis = database_manager.get_analysis(analysis_id)

    if form.validate_on_submit():
        description = form.description.data
        admin_ids = form.admin_ids.data
        expert_ids = form.expert_ids.data

        analysis = database_manager.update_analysis(
            analysis_id=analysis_id,
            description=description,
            administrators=admin_ids,
            experts=expert_ids,
        )

        if analysis:
            flash("Análise atualizada com sucesso.", "success")
            return redirect(
                url_for("analysis.get_analysis", analysis_id=analysis.id),
            )
        else:
            flash("Ocorreu um erro ao atualizar a análise.", "danger")

    return render_template("analysis/edit.html", form=form, analysis=analysis)


@bp.route("/criar", methods=["GET", "POST"])
@login_required
# @proxy_access(kind_object="analysis", kind_access="create")
def create_analysis():
    form = AnalysisForm()
    if form.validate_on_submit():
        description = form.description.data
        admin_ids = form.admin_ids.data

        analysis = database_manager.create_analysis(
            description=description, administrators=admin_ids
        )

        if analysis:
            flash("Análise criada com sucesso.", "success")
            return redirect(
                url_for("analysis.get_analysis", analysis_id=analysis.id),
            )
        else:
            flash("Ocorreu um erro ao criar a análise.", "danger")

    return render_template("analysis/create.html", form=form)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
