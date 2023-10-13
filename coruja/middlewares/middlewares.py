from datetime import datetime

from flask import Flask, flash, redirect, request
from flask_login import current_user

from ..extensions.auth import login_manager
from ..extensions.database import db
from ..models import AccessLog


def init_middlware_login(app: Flask):
    app.register_error_handler(404, handle_404)
    app.before_request(_before_request)


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash("Por favor, faça login antes de acessar a página :D", "danger")

    return redirect("/login")


def _before_request():
    if current_user.is_authenticated and not request.path.startswith(
        "/static/"
    ):
        current_user.last_seen = datetime.utcnow()
        new_access_log = AccessLog(
            ip=request.remote_addr,
            user_agent=request.user_agent.string,
            access_at=datetime.utcnow(),
            endpoint=request.path,
            user_id=current_user.id,
        )
        db.session.add(new_access_log)
        db.session.commit()


def handle_404(e):
    return redirect("/home")
