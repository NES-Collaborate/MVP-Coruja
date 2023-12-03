from datetime import datetime

from flask import Flask, flash, redirect, request, url_for
from flask_login import current_user
from werkzeug.exceptions import Forbidden, NotFound

from ..extensions.auth import login_manager
from ..extensions.database import db
from ..models import AccessLog, User


@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    """Carrega um determinado usuário por ID

    Args:
        user_id (int): ID do usuário

    Returns:
        User: Usuário
        None: Se o usuário não foi encontrado
    """
    return User.query.filter_by(id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized_handler():
    """Trata o caso de usuário não estar logado (não autorizado)"""
    flash("Faça login antes de acessar a página", "danger")

    return redirect(
        url_for("auth.login", next=request.path)
    )


def _before_request():
    """Função chamada antes de cada requisição"""
    is_static = request.path.startswith("/static/")
    is_favicon = request.path.startswith("/favicon.ico")
    if current_user.is_authenticated and not (is_static or is_favicon):  # type: ignore
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
    """Trata erros 404

    Args:
        err (NotFound): Erro
    """
    if (
        err.description != NotFound.description
        and err.description
    ):
        flash(err.description, "warning")
    else:
        flash(
            "A página que você procura não foi encontrada",
            "warning",
        )
    return redirect(url_for("application.home"))


def handle_403(err: Forbidden):
    """Trata erros 403

    Args:
        err (Forbidden): Erro
    """
    if (
        err.description != Forbidden.description
        and err.description
    ):
        flash(err.description, "warning")
    else:
        flash(
            (
                "Você não tem permissão para acessar esta"
                " página"
            ),
            "danger",
        )
    return redirect(url_for("application.home"))


def init_middleware_login(app: Flask) -> None:
    app.register_error_handler(404, handle_404)
    app.register_error_handler(403, handle_403)
    app.before_request(_before_request)
