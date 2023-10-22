from flask import Blueprint, Flask, render_template
from flask_login import login_required

from ..decorators import proxy_access
from ..utils import database_manager

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
        analysis_risk=analysis_risk,
        actives=actives,
    )


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
