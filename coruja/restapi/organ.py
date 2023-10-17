from flask import (
    Blueprint,
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from ..forms import OrganForm
from ..utils import database_manager, form_to_dict

bp = Blueprint("organ", __name__, url_prefix="/organ")


@bp.route("/create", methods=["GET", "POST"])
@login_required
def get_post_organ_creation():
    form = OrganForm()

    if not database_manager.is_organ_administrator(current_user):
        abort(403)

    elif request.method == "POST":
        if form.validate_on_submit():
            organ = form_to_dict(form)
            database_manager.add_organ(**organ, administrators=[current_user])

            flash(f"Orgão {organ.get('name')!r} criado com sucesso", "success")
        else:
            flash("Encontramos um erro ao tentar criar o órgão", "danger")

        return redirect(url_for("application.home"))

    return render_template("organ/create.html", form=form)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
