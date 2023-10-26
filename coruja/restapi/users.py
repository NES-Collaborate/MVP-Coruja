from typing import Any, Dict

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
from ..utils import (
    contains_permission,
    database_manager,
    form_to_dict,
    get_name_role,
    get_role,
    get_role_lower_hierarchy,
)

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/<int:user_id>")
@login_required
# @proxy_access(kind_object="user", kind_access="read")
def get_user(user_id: int):
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
    atual não tiver permissão de criar usuários, será retornado um erro 403.
    """
    if not contains_permission(current_user.role, "user", "create"):  # type: ignore
        abort(403)

    form = UserForm()

    if request.method == "POST" and form.validate_on_submit():
        user: Dict[str, str | Any] = form_to_dict(form)["data"]
        user.pop("csrf_token", None)
        user.pop("submit", None)

        role_name = get_name_role(user["role"], reversed=True)
        user["role"] = get_role(role_name)

        database_manager.add_user(**user)
        flash(f"Usuário {user.get('name')} criado", "success")
        return redirect(url_for("application.home"))

    user_role = get_name_role(get_role_lower_hierarchy(current_user.role))  # type: ignore
    return render_template("users/create.html", form=form, role=user_role)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
