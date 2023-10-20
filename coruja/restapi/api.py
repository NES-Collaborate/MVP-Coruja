from flask import Blueprint, Flask, jsonify, request
from flask_login import login_required
from sqlalchemy import or_

from ..models import User

bp = Blueprint("api", __name__, url_prefix="/api/v1")


@bp.route("/get-users")
@login_required
def get_users():
    """Obtém uma lista de usuários com base em uma busca.

    Returns:
        Uma resposta JSON contendo uma lista de usuários que correspondem aos
        critérios de busca. A resposta tem a seguinte estrutura:
        >>> {
        ...    "users": [
        ...        {
        ...            "id": int,
        ...            "name": str,
        ...            "cpf": str,
        ...            "title": str
        ...        },
        ...        ...
        ...    ]
        ... }
    """
    query = request.args.get("query", "")
    users: list[User] = User.query.filter(
        or_(
            User.name.ilike(f"%{query}%"),  # type: ignore
            User.cpf.ilike(f"%{query}%"),  # type: ignore
            User.email_personal.ilike(f"%{query}%"),  # type: ignore
            User.email_professional.ilike(f"%{query}%"),  # type: ignore
        )
    ).all()

    _users = [user.as_dict(["id", "name", "cpf", "title"]) for user in users]
    return jsonify({"users": _users})


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
