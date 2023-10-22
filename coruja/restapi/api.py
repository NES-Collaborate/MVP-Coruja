from flask import Blueprint, Flask, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import or_

from coruja.decorators.proxy import can_access_analysis_risk

from ..models import User
from ..utils import database_manager

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


@bp.route("/get-actives", methods=["POST"])
@login_required
def get_actives():
    data = request.get_json()
    if "ar_id" not in data:
        return jsonify({"error": "Missing analysis_risk_id"}), 400

    analysis_risk = None
    if can_access_analysis_risk(data["ar_id"], current_user):  # type: ignore [current_user isn't None]
        analysis_risk = database_manager.get_analysis_risk(
            data["ar_id"], or_404=False
        )
    else:
        return (
            jsonify({"error": "You don't have access to this analysis_risk"}),
            403,
        )

    _actives = analysis_risk.associated_actives  # type: ignore [analysis_risk isn't None]

    return jsonify({"actives": [active.as_dict() for active in _actives]})  # type: ignore


@bp.route("/get-threats", methods=["POST"])
@login_required
def get_threats():
    data = request.get_json()
    if "ac_id" not in data or "ar_id" not in data:
        return jsonify({"error": "Missing active_id or analysis_risk_id"}), 400

    if not can_access_analysis_risk(data["ar_id"], current_user):  # type: ignore [current_user isn't None]
        return (
            jsonify({"error": "You don't have access to this analysis_risk"}),
            403,
        )

    _active = database_manager.get_active(data["ac_id"], or_404=False)
    if not _active:
        return jsonify({"error": "Active not found"}), 404

    _result = {threat.id: {"title": threat.title, "description": threat.description, "adverses_actions": []} for threat in _active.associated_threats}  # type: ignore

    for _id in _result:
        _result[_id][
            "adverses_actions"
        ] = database_manager.get_adverse_actions(threat_id=_id)

    return jsonify(_result)


@bp.route("/update-adveser-action-score", methods=["POST"])
@login_required
def update_adverse_action_score():
    return ""


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
