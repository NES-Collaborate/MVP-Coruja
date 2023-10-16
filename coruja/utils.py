from sqlalchemy.orm import aliased

from .extensions.database import db
from .models import Organ, organ_administrators


def get_organs_by_user_id(user_id: int) -> list[Organ]:
    """
    Obtém órgãos associados a um usuário com base em seu ID.

    Parâmetros:
    user_id (int): O ID do usuário a ser pesquisado.

    Retorna:
    list[Organ]: Uma lista de objetos Organ associados ao usuário especificado.
    """
    organ_admin_alias = aliased(organ_administrators)

    organs = (
        Organ.query.join(
            organ_admin_alias,
            Organ.id == organ_admin_alias.c.organ_id,
        )
        .filter(organ_admin_alias.c.user_id == user_id)
        .all()
    )

    return organs


def insert_organ(**kwargs) -> None:
    administrators = kwargs.pop("administrators", [])
    orgao = Organ(**kwargs)
    db.session.add(orgao)
    db.session.commit()

    orgao.administrators.extend(administrators)

    db.session.commit()
    db.session.commit()