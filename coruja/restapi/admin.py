from flask import Blueprint, Flask, render_template, request
from flask_login import login_required

from ..models import AccessLog

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/", methods=["GET"])
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


def init_api(app: Flask):
    app.register_blueprint(bp)
