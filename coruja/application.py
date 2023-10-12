from flask import Blueprint, render_template, abort, flash, url_for, redirect
from flask_login import login_required, current_user
from .helpers import get_orgaos_by_user_id, insert_orgao
from .forms import OrgaoForm


bp = Blueprint("application", __name__, url_prefix="/app")


@bp.route("/home")
@login_required
def home():
    form = OrgaoForm()
    orgaos = get_orgaos_by_user_id(current_user.id)
    return render_template("application/home.html", orgaos=orgaos, form=form)


@bp.route("/criar-orgao", methods=["POST"])
@login_required
def create_orgao():
    if not current_user.is_adm:
        abort(403)

    form = OrgaoForm()
    if form.validate_on_submit():
        keys = ["name", "cnpj", "address", "email", "telephone"]
        orgao = {key: getattr(form, key).data for key in keys}
        insert_orgao(**orgao, administrators=[current_user])
        flash("Orgão criado com sucesso!", "success")
    else:
        flash("Erro ao criar orgão!", "danger")

    return redirect(url_for("application.home"))
