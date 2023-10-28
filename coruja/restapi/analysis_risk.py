from asyncio import log

from flask import Blueprint, Flask, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..decorators import proxy_access
from ..forms import DefaultForm
from ..utils import database_manager, form_to_dict

bp = Blueprint("analysis_risk", __name__, url_prefix="/analise-risco")


@bp.route("/<int:analysis_risk_id>")
@login_required
@proxy_access(kind_object="analysis_risk", kind_access="read")
def get_analysis_risk(analysis_risk_id: int):
    """Rota para obter uma analise de risco, deve renderizar uma página
    dinâmica para atribuição de notas

    Args:
        analysis_risk_id (int): ID da analise
    """

    analysis_risk = database_manager.get_analysis_risk(analysis_risk_id)

    actives = analysis_risk.associated_actives  # type: ignore [analysis_risk isn't None]

    return render_template(
        "analysis_risk/analysis_risk.html",
        analysis_risk=analysis_risk,  # type: ignore
        actives=actives,
    )


@bp.route("/ativo/criar", methods=["GET", "POST"])
@login_required
def create_active():
    """Rota para criar um ativo"""

    form = DefaultForm()
    parent_id = request.args.get("parent_id", default=None, type=int)
    if not parent_id:
        flash("Análise de Risco não especificada", "danger")
        return redirect(url_for("application.home"))

    @proxy_access(kind_object="analysis_risk", kind_access="update")
    def get_analysis_risk(*, analysis_risk_id: int):
        return database_manager.get_analysis_risk(analysis_risk_id)

    analysis_risk = get_analysis_risk(analysis_risk_id=parent_id)

    if request.method == "POST" and form.validate_on_submit():
        active_data = form_to_dict(form)["data"]
        for field in ["csrf_token", "submit"]:
            active_data.pop(field, None)

        active = database_manager.add_active(
            **active_data,
        )

        analysis_risk.add_active(active)  # type: ignore

        return redirect(
            url_for(
                "analysis_risk.get_analysis_risk", analysis_risk_id=analysis_risk.id  # type: ignore
            )
        )

    return render_template("analysis_risk/create_active.html", form=form)


@bp.route("/ameaca/criar", methods=["GET", "POST"])
@login_required
def create_threat():
    """Rota para criar uma ameaça"""
    form = DefaultForm()
    parent_id = request.args.get("parent_id", default=None, type=int)
    if not parent_id:
        flash("Análise de Risco não especificada", "danger")
        return redirect(url_for("application.home"))

    @proxy_access(kind_object="active", kind_access="update")
    def get_active(*, active_id: int):
        return database_manager.get_active(active_id)

    active = get_active(active_id=parent_id)

    if request.method == "POST" and form.validate_on_submit():
        threat_data = form_to_dict(form)["data"]
        for field in ["csrf_token", "submit"]:
            threat_data.pop(field, None)

        threat = database_manager.add_threat(
            **threat_data,
        )

        active.add_threat(threat)  # type: ignore

        return redirect(
            url_for(
                "analysis_risk.get_analysis_risk", analysis_risk_id=active.analysis_risk_id  # type: ignore
            )
        )

    return render_template("analysis_risk/create_threat.html", form=form)


@bp.route("/acao-adversa/criar", methods=["GET", "POST"])
@login_required
def create_adverse_action():
    """Rota para criar ação adversa"""

    form = DefaultForm()

    parent_id = request.args.get("parent_id", default=None, type=int)
    if not parent_id:
        flash("Ameaça não especificada", "danger")
        return redirect(url_for("application.home"))

    @proxy_access(kind_object="threat", kind_access="update")
    def get_threat(*, threat_id: int):
        return database_manager.get_threat(threat_id)

    threat = get_threat(threat_id=parent_id)

    @proxy_access(kind_object="active", kind_access="update")
    def get_active(*, active_id: int):
        return database_manager.get_active(active_id)

    active = get_active(active_id=threat.active_id)  # type: ignore

    if request.method == "POST" and form.validate_on_submit():
        adverse_action_data = form_to_dict(form)["data"]
        for field in ["csrf_token", "submit"]:
            adverse_action_data.pop(field, None)

        adverse_action = database_manager.add_adverse_action(
            **adverse_action_data,
        )

        threat.add_adverse_action(adverse_action)  # type: ignore

        return redirect(
            url_for(
                "analysis_risk.get_analysis_risk", analysis_risk_id=active.analysis_risk_id  # type: ignore
            )
        )

    return render_template(
        "analysis_risk/create_adverse_action.html", form=form
    )


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
