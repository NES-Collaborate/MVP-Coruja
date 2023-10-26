from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
def index():
    """Rota principal de admin"""
    if current_user.role.name == "admin":  # type: ignore
        return render_template("admin/index.html")
    else:
        abort(403)
