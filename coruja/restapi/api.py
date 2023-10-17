from flask import Blueprint, Flask, jsonify, request
from flask_login import login_required
from sqlalchemy import or_

from ..models import User

bp = Blueprint("api", __name__, url_prefix="/api/v1")


@bp.route("/get-users")
@login_required
def get_users():
    query = request.args.get("query", "")
    users: list[User] = User.query.filter(
        or_(
            User.name.ilike(f"%{query}%"),
            User.cpf.ilike(f"%{query}%"),
            User.email_personal.ilike(f"%{query}%"),
            User.email_professional.ilike(f"%{query}%"),
        )
    ).all()
    result = {
        "users": [
            user.as_dict(
                filter_params=["id", "name", "cpf", "title"],
            )
            for user in users
        ]
    }
    return jsonify(result)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
