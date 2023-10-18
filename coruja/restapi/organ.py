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

from ..forms import OrganForm
from ..utils import database_manager, form_to_dict

bp = Blueprint("organ", __name__, url_prefix="/orgao")


@bp.route("/criar", methods=["GET", "POST"])
@login_required
def get_post_organ_creation():
    """
    Rota para criar um novo órgão.

    Esta rota é acessível através dos métodos GET e POST. Se o usuário
    atual não for um administrador de órgãos, será retornado um erro 403.
    """
    if not database_manager.is_organ_administrator(current_user):
        abort(403)

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
        flash(f"Orgão {organ.get('name')!r} criado com sucesso", "success")
        return redirect(url_for("application.home"))

    flash("Encontramos um erro ao tentar criar o órgão", "danger")
    return render_template("organ/create.html", form=form)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
