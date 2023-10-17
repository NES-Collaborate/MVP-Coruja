from flask import Blueprint, Flask, render_template
from flask_login import login_required

from ..utils import database_manager

bp = Blueprint("analysis", __name__, url_prefix="/analise")


@bp.route("/<int:analysis_id>")
@login_required
def get_analysis(analysis_id: int):
    analysis = database_manager.get_analysis_by_id(analysis_id)
    # TODO: Criar métodos para retornar uma lista de experts com seus respectivos
    # "progressos" dentro de uma determinada análise (notasDadas/notasPossíveis)
    experts = analysis.experts
    context = {"analysis": analysis, "experts": experts}
    return render_template("analysis/analysis.html", **context)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
