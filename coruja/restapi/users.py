from typing import Dict

import ipdb
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

from ..forms import UserForm
from ..utils import database_manager, form_to_dict

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/<int:user_id>")
@login_required
# @proxy_access(kind_object="user", kind_access="read")
def get_organ(user_id: int):
    """Rota para retornar a página de detalhes de um usuário.

    Args:
        user_id (int): ID do usuário a ser visualizado.
    """
    user = database_manager.get_user(user_id)
    return render_template("users/users.html", user=user)


@bp.route("/create/", methods=["GET", "POST"])
@login_required
def create_user():
    """
    Rota para criar um novo usuário.

    Esta rota é acessível através dos métodos GET e POST. Se o usuário
    atual não for um administrador de órgãos, será retornado um erro 403.
    """
    if not database_manager.is_organ_administrator(current_user):
        abort(403)

    form = UserForm()

    if request.method == "POST":
        ipdb.set_trace()
        if form.validate_on_submit():
            user: Dict[str, str | bool] = form_to_dict(form)["data"]
            user.pop("csrf_token", None)
            user.pop("submit", None)

            database_manager.add_user(**user)
            flash(f"Usuário {user.get('name')} criado", "success")
            return redirect(url_for("application.home"))

    return render_template("users/create.html", form=form)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
