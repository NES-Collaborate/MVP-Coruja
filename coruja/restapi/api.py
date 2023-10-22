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

    # _result = {
    #     "id1": {
    #         "title": "Threat 1",
    #         "description": "This is the description for Threat 1",
    #         "adverse_actions": {
    #             "id_1": {"title": "Action 1", "description": "Description 1", "score": 5},
    #             "id_2": {"title": "Action 2", "description": "Description 2", "score": 3}
    #         }
    #     },
    #     "id2": {
    #         "title": "Threat 2",
    #         "description": "This is the description for Threat 2",
    #         "adverse_actions": {
    #             "id_3": {"title": "Action 3", "description": "Description 3", "score": 4},
    #             "id_4": {"title": "Action 4", "description": "Description 4", "score": 2}
    #         }
    #     },
    #     "id3": {
    #         "title": "Threat 3",
    #         "description": "This is the description for Threat 3",
    #         "adverse_actions": {
    #             "id_5": {"title": "Action 5", "description": "Description 5", "score": 1},
    #             "id_6": {"title": "Action 6", "description": "Description 6", "score": 6}
    #         }
    #     },
    #     "id4": {
    #         "title": "Threat 4",
    #         "description": "This is the description for Threat 4",
    #         "adverse_actions": {
    #             "id_7": {"title": "Action 7", "description": "Description 7", "score": 3},
    #             "id_8": {"title": "Action 8", "description": "Description 8", "score": 5}
    #         }
    #     },
    #     "id5": {
    #         "title": "Threat 5",
    #         "description": "This is the description for Threat 5",
    #         "adverse_actions": {
    #             "id_9": {"title": "Action 9", "description": "Description 9", "score": 2},
    #             "id_10": {"title": "Action 10", "description": "Description 10", "score": 7}
    #         }
    #     },
    #     "id6": {
    #         "title": "Threat 6",
    #         "description": "This is the description for Threat 6",
    #         "adverse_actions": {
    #             "id_11": {"title": "Action 11", "description": "Description 11", "score": 4},
    #             "id_12": {"title": "Action 12", "description": "Description 12", "score": 1}
    #         }
    #     },
    #     "id7": {
    #         "title": "Threat 7",
    #         "description": "This is the description for Threat 7",
    #         "adverse_actions": {
    #             "id_13": {"title": "Action 13", "description": "Description 13", "score": 5},
    #             "id_14": {"title": "Action 14", "description": "Description 14", "score": 6}
    #         }
    #     },
    #     "id8": {
    #         "title": "Threat 8",
    #         "description": "This is the description for Threat 8",
    #         "adverse_actions": {
    #             "id_15": {"title": "Action 15", "description": "Description 15", "score": 2},
    #             "id_16": {"title": "Action 16", "description": "Description 16", "score": 8}
    #         }
    #     },
    #     "id9": {
    #         "title": "Threat 9",
    #         "description": "This is the description for Threat 9",
    #         "adverse_actions": {
    #             "id_17": {"title": "Action 17", "description": "Description 17", "score": 3},
    #             "id_18": {"title": "Action 18", "description": "Description 18", "score": 4}
    #         }
    #     },
    #     "id10": {
    #         "title": "Threat 10",
    #         "description": "This is the description for Threat 10",
    #         "adverse_actions": {
    #             "id_19": {"title": "Action 19", "description": "Description 19", "score": 5},
    #             "id_20": {"title": "Action 20", "description": "Description 20", "score": 1}
    #         }
    #     }
    # }

    return jsonify(_result)


def init_api(app: Flask) -> None:
    app.register_blueprint(bp)
