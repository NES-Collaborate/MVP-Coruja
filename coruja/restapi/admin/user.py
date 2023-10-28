from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...models import User
from ...utils import database_manager
from ...decorators import proxy_access
bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/", methods=["GET"])
@login_required
@proxy_access(kind_object="admin", kind_access="read", has_obj_id=False)
def show_users():
    page = request.args.get("page", 1, type=int)
    users = User.query.paginate(
        page=page, per_page=10
    )  # 10 usuários por página
    return render_template(
        "admin/users.html", users=users.items, pagination=users
    )


@bp.route("/<int:user_id>/info", methods=["GET"])
@login_required
@proxy_access(kind_object="admin", kind_access="read", has_obj_id=False)
def user_info(user_id: int):
    """Rota para exibir informações de um usuário específico pelo seu ID.

    Args:
        user_id (int): ID do usuário cujas informações serão exibidas.
    """
    user = database_manager.get_user(
        user_id
    )  # Supondo que você tem uma função que pega o usuário pelo ID

    if not user:
        flash("Usuário não encontrado", "error")
        return redirect(
            url_for("user_list")
        )  # Supondo que você tem uma rota para listar usuários

    return render_template("admin/user_info.html", user=user)
