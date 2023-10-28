from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...forms import VulnerabilityCategoryForm
from ...models import VulnerabilityCategory
from ...utils import database_manager
from ...decorators import proxy_access
bp = Blueprint("category", __name__, url_prefix="/categoria")


@bp.route("/", methods=["GET"])
@login_required
@proxy_access(kind_object="admin", kind_access="read", has_obj_id=False)
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


@bp.route("/criar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="admin", kind_access="create", has_obj_id=False)
def create_category():
    form = VulnerabilityCategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        database_manager.add_vulnerability_category(name)  # type: ignore
        flash(f"Categoria {name} criado com sucesso", "success")
        return redirect(url_for("admin.category.view_categories"))
    return render_template("admin/create_category.html", form=form)


@bp.route("/<int:category_id>/editar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="admin", kind_access="update", has_obj_id=False)
def edit_category(category_id: int):
    category = database_manager.get_category(category_id)
    if not category:
        flash("Categoria não encontrada.", "error")
        return redirect(url_for("admin.category.view_categories"))

    form = VulnerabilityCategoryForm(obj=category)

    if form.validate_on_submit():
        form_data = {"name": form.name.data}
        updated_category = database_manager.update_vulnerability_category(
            category, form_data  # type: ignore
        )
        if updated_category:
            flash(
                f"Categoria {updated_category.name} editada com sucesso.",
                "success",
            )
            return redirect(
                url_for(
                    "admin.category.view_categories",
                )
            )

    return render_template(
        "admin/edit_category.html", form=form, category=category
    )
