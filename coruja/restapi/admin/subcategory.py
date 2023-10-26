from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from ...forms import VulnerabilitySubcategoryForm
from ...utils import database_manager

bp = Blueprint("subcategory", __name__, url_prefix="/subcategorias")


@bp.route("/criar", methods=["GET", "POST"])
@login_required
def create_subcategory():
    form = VulnerabilitySubcategoryForm()
    if form.validate_on_submit():
        name = (
            form.name.data
        )  # Usando form.name.data em vez de request.form.get("name")
        database_manager.add_vulnerability_subcategory(name)  # type: ignore
        flash(f"Subcategoria {name} criado com sucesso", "success")
        return redirect(url_for("admin_configurations.view_categories"))
    return render_template("admin/create_subcategory.html", form=form)
