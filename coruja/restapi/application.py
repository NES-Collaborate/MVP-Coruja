from flask import Blueprint, Flask, render_template
from flask_login import current_user, login_required

from ..forms import OrganForm
from ..utils import database_manager

bp = Blueprint("application", __name__, url_prefix="/app")


@bp.route("/home")
@login_required
def home():
    """Rota principal da aplicação
    """
    form = OrganForm()
    organs = database_manager.get_organs(getattr(current_user, "id"))

    return render_template(
        "application/home.html",
        organs=organs,
        form=form,
    )


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
