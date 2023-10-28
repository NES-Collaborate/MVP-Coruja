import csv
from io import StringIO

from flask import Blueprint, Response, render_template, request, stream_with_context
from flask_login import login_required

from ...models import AccessLog, Change
from ...decorators import proxy_access

bp = Blueprint("logs", __name__, url_prefix="/logs")


@bp.route("/acesso", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="admin", kind_access="read", has_obj_id=False)
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
@proxy_access(kind_object="admin", kind_access="read", has_obj_id=False)
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


def generate_csv_chunks_acess():
    output = StringIO()
    writer = csv.writer(output)
    headers = [
        "User Name",
        "User CPF",
        "IP",
        "User Agent",
        "Access At",
        "Endpoint",
    ]
    writer.writerow(headers)
    yield output.getvalue()
    output.truncate(0)
    output.seek(0)

    page = 1
    per_page = 100

    while True:
        all_logs = AccessLog.query.paginate(
            page=page, per_page=per_page, error_out=False
        ).items  # Substitua isso com sua própria lógica de consulta
        if not all_logs:
            break

        for log in all_logs:
            user_name = log.user.name
            user_cpf = log.user.cpf_censored
            ip = log.ip
            user_agent = log.user_agent
            access_at = log.access_at.strftime("%d/%m/%Y %H:%M:%S")
            endpoint = log.endpoint

            writer.writerow(
                [user_name, user_cpf, ip, user_agent, access_at, endpoint]
            )

        yield output.getvalue()
        output.truncate(0)
        output.seek(0)

        page += 1


@bp.route("/download_logs", methods=["POST", "GET"])
@login_required
@proxy_access(kind_object="admin", kind_access="read", has_obj_id=False)
def download_logs():
    headers = {
        "Content-Disposition": "attachment; filename=access_logs.csv",
        "Content-Type": "text/csv",
    }

    return Response(
        stream_with_context(generate_csv_chunks_acess()), headers=headers
    )


def generate_csv_chunks():
    output = StringIO()
    writer = csv.writer(output)
    headers = ["Usuário", "Objeto", "Alterações"]
    writer.writerow(headers)
    yield output.getvalue()
    output.truncate(0)
    output.seek(0)

    page = 1
    per_page = 100

    while True:
        all_changes = Change.query.paginate(
            page=page, per_page=per_page, error_out=False
        ).items  # Substitua isso com sua própria lógica de consulta
        if not all_changes:
            break

        for change in all_changes:
            user_name = change.user.name
            user_cpf = change.user.cpf_censored
            object_type = change.object_type
            object_old = change.object_old
            object_new = change.object_new

            changes = []
            for key, value_old in object_old.items():
                value_new = object_new.get(key, None)
                if value_old != value_new:
                    change_str = f"[{key}] {value_old!r} -> {value_new!r}\n"
                    changes.append(change_str)

            changes_str = "".join(changes).strip()
            usuario = f"{user_name} - {user_cpf}"
            writer.writerow([usuario, object_type, changes_str])

        yield output.getvalue()
        output.truncate(0)
        output.seek(0)

        page += 1


@bp.route("/download_changes", methods=["POST", "GET"])
@login_required
@proxy_access(kind_object="admin", kind_access="read", has_obj_id=False)
def download_changes():
    headers = {
        "Content-Disposition": "attachment; filename=change_logs.csv",
        "Content-Type": "text/csv",
    }

    return Response(
        stream_with_context(generate_csv_chunks()), headers=headers
    )
