import csv
from io import StringIO

from flask import (
    Blueprint,
    Flask,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from ..forms import VulnerabilityCategoryForm, VulnerabilitySubcategoryForm
from ..models import (
    AccessLog,
    Change,
    Vulnerability,
    VulnerabilityCategory,
    VulnerabilitySubCategory,
)
from ..utils import database_manager

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
def index():
    """Rota principal de admin"""
    if current_user.role.name == "admin":  # type: ignore
        return render_template("admin/index.html")
    else:
        abort(403)


@bp.route("/logs-acesso", methods=["GET", "POST"])
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


@bp.route("/changes", methods=["GET"])
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


@bp.route("/download_logs", methods=["POST", "GET"])
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


bp2 = Blueprint("admin_configurations", __name__, url_prefix="/admin/config")


@bp2.route("/categorias", methods=["GET"])
@login_required
def view_categories():
    """Visualização das categorias de vulnerabilidades"""
    page = request.args.get("page", 1, type=int)
    pagination = VulnerabilityCategory.query.paginate(page=page, per_page=10)
    all_categories = pagination.items
    return render_template(
        "admin/categories.html",
        categories=all_categories,
        pagination=pagination,
        has_prev_page=pagination.has_prev,
        has_next_page=pagination.has_next,
    )


@bp2.route("/category_form", methods=["GET", "POST"])
@login_required
def category_form():
    form = VulnerabilityCategoryForm()
    if form.validate_on_submit():
        name = (
            form.name.data
        )  # Usando form.name.data em vez de request.form.get("name")
        database_manager.add_vulnerability_category(name)  # type: ignore
        flash(f"Categoria {name} criado com sucesso", "success")
        return redirect(url_for("admin_configurations.view_categories"))
    return render_template("admin/category_form.html", form=form)


"""
@bp.route("/subcategorias-vulnerabilidades", methods=["GET"])
@login_required
def list_vulnerability_subcategories():
    pass

"""


@bp.route("/nova-subcategorias-vulnerabilidades", methods=["GET", "POST"])
@login_required
def create_vulnerability_subcategories():
    form = VulnerabilitySubcategoryForm()
    if form.validate_on_submit():
        name = (
            form.name.data
        )  # Usando form.name.data em vez de request.form.get("name")
        database_manager.add_vulnerability_subcategory(name)  # type: ignore
        flash(f"Subcategoria {name} criado com sucesso", "success")
        return redirect(url_for("admin_configurations.view_categories"))
    return render_template(
        "admin/create_vulnerability_subcategory.html", form=form
    )


def init_api(app: Flask):
    app.register_blueprint(bp)
    app.register_blueprint(bp2)
