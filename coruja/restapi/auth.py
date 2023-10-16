from flask import (
    Blueprint,
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user

from ..forms import LoginForm
from ..models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(cpf=form.cpf.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login bem-sucedido!", "success")
            next = request.args.get("next") or url_for("application.home")
            return redirect(next)
        else:
            flash("CPF ou Senha incorretos", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout bem-sucedido!", "success")
    return redirect(url_for("auth.login"))


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)