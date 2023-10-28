from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...decorators import proxy_access
from ...forms import VulnerabilitySubcategoryForm
from ...models import VulnerabilitySubCategory
from ...utils import database_manager

bp = Blueprint("subcategory", __name__, url_prefix="/subcategoria")


@bp.route("/", methods=["GET"])
@login_required
@proxy_access(kind_object="admin", kind_access="read", has_obj_id=False)
def view_subcategories():
    """Visualização das categorias de vulnerabilidades"""
    try:
        category_id = request.args.get("category_id", None, type=int)
    except ValueError:
        flash("ID da categoria de vulnerabilidades não informado", "error")
    else:
        if not category_id:
            flash("Categoria de vulnerabilidades não encontrada", "error")
            return redirect(url_for("admin.subcategory.view_categories"))
        
    page = request.args.get("page", 1, type=int)
    pagination = VulnerabilitySubCategory.query.filter_by(
        category_id=category_id
    ).paginate(page=page, per_page=10)
    all_subcategories = pagination.items
    return render_template(
        "admin/subcategories.html",
        subcategories=all_subcategories,
        pagination=pagination,
        has_prev_page=pagination.has_prev,
        has_next_page=pagination.has_next,
        category_id=category_id,
    )


@bp.route("/criar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="admin", kind_access="create", has_obj_id=False)
def create_subcategory():
    try:
        category_id = request.args.get("category_id", None, type=int)
    except ValueError:
        flash("ID da categoria de vulnerabilidades não informado", "error")
    else:
        if not category_id:
            flash("Categoria de vulnerabilidades não encontrada", "error")
            return redirect(url_for("admin.subcategory.view_categories"))
    form = VulnerabilitySubcategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        database_manager.add_vulnerability_subcategory(name, category_id)  # type: ignore
        flash(f"Subcategoria {name} criado com sucesso", "success")
        return redirect(
            url_for(
                "admin.subcategory.view_subcategories", category_id=category_id
            )
        )
    return render_template("admin/create_subcategory.html", form=form)


@bp.route("/<int:subcategory_id>/editar", methods=["GET", "POST"])
@login_required
@proxy_access(kind_object="admin", kind_access="update", has_obj_id=False)
def edit_subcategory(subcategory_id: int):
    subcategory = database_manager.get_subcategory(subcategory_id)
    if not subcategory:
        flash("Categoria não encontrada.", "error")
        return redirect(url_for("admin.subcategory.view_categories"))

    form = VulnerabilitySubcategoryForm(obj=subcategory)

    if form.validate_on_submit():
        form_data = {"name": form.name.data}
        updated_category = database_manager.update_vulnerability_subcategory(
            subcategory, form_data  # type: ignore
        )
        if updated_category:
            flash(
                f"Categoria {updated_category.name} editada com sucesso.",
                "success",
            )
            return redirect(
                url_for(
                    "admin.subcategory.view_subcategories",
                )
            )
    return render_template(
        "admin/edit_subcategory.html", form=form, subcategory=subcategory
    )
