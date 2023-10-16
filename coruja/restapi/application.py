from flask import (
    Blueprint,
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required

from ..forms import OrgaoForm
from ..utils import get_organs_by_user_id, insert_organ

bp = Blueprint("application", __name__, url_prefix="/app")


@bp.route("/home")
@login_required
def home():
    form = OrgaoForm()
    orgaos = get_organs_by_user_id(current_user.id)  # type: ignore

    return render_template("application/home.html", orgaos=orgaos, form=form)


@bp.route("/criar-orgao", methods=["POST"])
@login_required
def create_orgao():
    if not current_user.is_adm:  # type: ignore
        abort(403)

    form = OrgaoForm()
    if form.validate_on_submit():
        keys = ["name", "cnpj", "address", "email", "telephone"]
        orgao = {key: getattr(form, key).data for key in keys}

        insert_organ(**orgao, administrators=[current_user])
        flash("Orgão criado com sucesso!", "success")
    else:
        flash("Erro ao criar orgão!", "danger")

    return redirect(url_for("application.home"))


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
