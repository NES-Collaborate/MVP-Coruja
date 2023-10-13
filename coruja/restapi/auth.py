from datetime import datetime

from flask import (Blueprint, Flask, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions.auth import login_manager
from ..forms import LoginForm
from ..models import User

# from .. import app
# from ..extensions.database import db
# from ..models import AccessLog

bp = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


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


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash("Por favor, faça login antes de acessar a página :D", "danger")
    return redirect(url_for("auth.login"))


# @app.before_request
# def before_request():
#     if current_user.is_authenticated and not request.path.startswith("/static/"):
#         current_user.last_seen = datetime.utcnow()
#         new_access_log = AccessLog(
#             ip=request.remote_addr,
#             user_agent=request.user_agent.string,
#             access_at=datetime.utcnow(),
#             endpoint=request.path,
#             user_id=current_user.id,
#         )
#         db.session.add(new_access_log)
#         db.session.commit()


# @app.errorhandler(404)
# def error_404(e):
#     return redirect(url_for("application.home"))
# @app.errorhandler(404)
# def error_404(e):
#     return redirect(url_for("application.home"))


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
