from sqlalchemy.orm import aliased

from .extensions.database import db
from .models import Orgao, orgao_administrators


def get_orgaos_by_user_id(user_id) -> None:
    orgao_admin_alias = aliased(orgao_administrators)
    orgaos = (
        Orgao.query.join(
            orgao_admin_alias, Orgao.id == orgao_admin_alias.c.orgao_id
        )
        .filter(orgao_admin_alias.c.user_id == user_id)
        .all()
    )
    return orgaos


def insert_orgao(**kwargs) -> None:
    administrators = kwargs.pop("administrators", [])
    orgao = Orgao(**kwargs)
    db.session.add(orgao)
    db.session.commit()

    orgao.administrators.extend(administrators)
    db.session.commit()
    db.session.commit()
