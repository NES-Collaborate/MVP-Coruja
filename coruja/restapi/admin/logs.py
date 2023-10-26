import csv
from io import StringIO

from flask import Blueprint, make_response, render_template, request
from flask_login import login_required

from ...models import AccessLog, Change

bp = Blueprint("logs", __name__, url_prefix="/logs")


@bp.route("/acesso", methods=["GET", "POST"])
@login_required
def get_logs():
    """Rota que renderiza os logs de acesso paginados"""
    query = AccessLog.query

    user_id = request.args.get("user_id", "")
    if user_id:
        query = query.filter_by(user_id=user_id)

    page = request.args.get("page", 1, type=int)
    pagination = query.paginate(page=page, per_page=10)
    all_access_logs = pagination.items

    return render_template(
        "admin/records.html",
        logs=all_access_logs,
        pagination=pagination,
        has_prev_page=pagination.has_prev,
        has_next_page=pagination.has_next,
    )


@bp.route("/Mudanças", methods=["GET"])
@login_required
def get_changes():
    """Página que renderiza os logs de mudanças paginados"""
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


@bp.route("/download", methods=["POST", "GET"])
@login_required
def download_logs():
    # Definir cabeçalhos CSV
    csv_list = [
        ["User Name", "User CPF", "IP", "User Agent", "Access At", "Endpoint"]
    ]
    all_logs = AccessLog.query.all()
    # Adicionar linhas CSV
    for log in all_logs:
        csv_list.append(
            [
                log.user.name,
                log.user.cpf_censored,
                log.ip,
                log.user_agent,
                log.access_at.strftime("%d/%m/%Y %H:%M:%S"),
                log.endpoint,
            ]
        )

    si = StringIO()
    cw = csv.writer(si)
    cw.writerows(csv_list)
    output = make_response(si.getvalue())
    output.headers[
        "Content-Disposition"
    ] = "attachment; filename=access_logs.csv"
    output.headers["Content-type"] = "text/csv"
    return output
