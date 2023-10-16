from typing import Any, Dict

from flask_wtf import FlaskForm
from sqlalchemy.orm import aliased

from .extensions.database import db
from .models import Organ, User, organ_administrators


def form_to_dict(form: FlaskForm) -> Dict[Any, Any]:
    _new_form = {}
    for atributte in dir(form):
        if callable(getattr(form, atributte)) or atributte.startswith("__"):
            continue

        _new_form[atributte] = getattr(form, atributte)

    return _new_form


class DatabaseManager:
    def __init__(self):
        self.__db = db

    def get_organs_by_user_id(self, user_id: int) -> list[Organ]:
        """
        Obtém órgãos associados a um usuário com base em seu ID.

        Params:
            user_id (int): O ID do usuário a ser pesquisado.

        Return:
            list[Organ]: Uma lista de objetos Organ associados ao usuário
                especificado.
        """
        organ_admin_alias = aliased(organ_administrators)

        return (
            Organ.query.join(
                organ_admin_alias,
                Organ.id == organ_admin_alias.c.organ_id,
            )
            .filter(organ_admin_alias.c.user_id == user_id)
            .all()
        )

    def add_organ(self, **kwargs) -> None:
        administrators = kwargs.pop("administrators", [])
        organ = Organ(**kwargs)

        self.__db.session.add(organ)
        self.__db.session.commit()

        organ.administrators.extend(administrators)

        self.__db.session.commit()
        self.__db.session.commit()

    def is_organ_administrator(self, user: User | Any) -> bool:
        organ_admin = aliased(organ_administrators)

        organs = (
            Organ.query.join(
                organ_admin,
                Organ.id == organ_admin.c["organ_id"],
            )
            .filter(organ_admin.c["user_id"] == user.id)
            .first()
        )

        return bool(organs)


database_manager = DatabaseManager()
