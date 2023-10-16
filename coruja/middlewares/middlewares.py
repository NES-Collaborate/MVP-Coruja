from datetime import datetime

from flask import Flask, flash, redirect, request, url_for
from flask_login import current_user
from werkzeug.exceptions import NotFound

from ..extensions.auth import login_manager
from ..extensions.database import db
from ..models import AccessLog, User


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash("Por favor, faça login antes de acessar a página", "danger")

    return redirect(url_for("auth.login"))


def _before_request():
    is_static = request.path.startswith("/static/")
    if current_user.is_authenticated and not is_static:  # type: ignore
        current_user.last_seen = datetime.utcnow()
        new_access_log = AccessLog(
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            access_at=datetime.utcnow(),
            endpoint=request.path,
            user_id=current_user.id,  # type: ignore
        )
        db.session.add(new_access_log)
        db.session.commit()

def handle_404(err: NotFound):
    if err.description != NotFound.description:
        flash(err.description, "danger")
    else:
        flash("Desculpe, a página que você procura não foi encontrada", "warning")
    return redirect(url_for("application.home"))


def handle_403(err):
    flash("Você não tem permissão para acessar esta página", "danger")
    return redirect(url_for("application.home"))


def init_middlware_login(app: Flask) -> None:
    app.register_error_handler(404, handle_404)
    app.register_error_handler(403, handle_403)
    app.before_request(_before_request)