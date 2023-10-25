import ipdb
from flask import Blueprint, Flask, render_template
from flask_login import current_user, login_required

from ..decorators import can_access_institution, proxy_access
from ..utils import database_manager

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/<int:user_id>")
@login_required
@proxy_access(kind_object="organ", kind_access="read")
def get_organ(user_id: int):
    """Rota para retornar a página de detalhes de um usuário.

    Args:
        user_id (int): ID do usuário a ser visualizado.
    """
    # ipdb.set_trace()
    user = database_manager.get_user(user_id)

    # _access = lambda institution: can_access_institution(
    #     institution.id, current_user
    # )
    # institutions = list(filter(_access, organ.institutions))  # type: ignore

    return render_template("users/users.html", user=user)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
