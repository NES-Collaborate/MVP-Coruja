from flask import Blueprint, render_template
from flask_login import login_required

from ...decorators import proxy_access

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
@proxy_access(kind_object="admin", kind_access="read", has_obj_id=False)
def index():
    """Rota principal de admin"""
    return render_template("admin/index.html")
