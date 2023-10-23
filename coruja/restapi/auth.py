from flask import Blueprint, Flask, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from ..forms import LoginForm
from ..models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Rota de login"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(cpf=form.cpf.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next = request.args.get("next") or url_for("application.home")
            return redirect(next)
        else:
            flash("CPF e/ou senha incorreto", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    """Rota de logout (deslogar)
    """
    logout_user()
    return redirect(url_for("auth.login"))


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
