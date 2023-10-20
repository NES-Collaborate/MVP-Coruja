from flask import Blueprint, Flask, render_template, request, abort
from flask_login import current_user, login_required

from ..models import AccessLog, Change

bp = Blueprint("admin", __name__, url_prefix="/admin")



@bp.route("/")
@login_required
def index():
    if current_user.role.name == "admin": # type: ignore
        return render_template("admin/index.html")
    else:
        abort(403)

@bp.route("/logs-acesso", methods=["GET"])
@login_required
def get_records():
    page = request.args.get("page", 1, type=int)
    pagination = AccessLog.query.paginate(page=page, per_page=10)
    all_access_logs = pagination.items
    return render_template(
        "admin/records.html",
        logs=all_access_logs,
        pagination=pagination,
        has_prev_page=pagination.has_prev,
        has_next_page=pagination.has_next,
    )

@bp.route("/changes", methods=["GET"])
@login_required
def get_changes():
    page = request.args.get("page", 1, type=int)
    pagination = Change.query.paginate(page=page, per_page=10)
    all_changes = pagination.items
    return render_template(
        "admin/changes.html",
        logs=all_changes,
        pagination=pagination,
        has_prev_page=pagination.has_prev,
        has_next_page=pagination.has_next,
    )

def init_api(app: Flask):
    app.register_blueprint(bp)
