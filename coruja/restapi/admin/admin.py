from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
def index():
    """Rota principal de admin"""
    return render_template("admin/index.html")
