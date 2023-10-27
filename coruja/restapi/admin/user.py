from flask import Blueprint, render_template, request

from ...models import User

bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/", methods=["GET"])
def show_users():
    page = request.args.get("page", 1, type=int)
    users = User.query.paginate(
        page=page, per_page=10
    )  # 10 usuários por página
    return render_template(
        "admin/users.html", users=users.items, pagination=users
    )
