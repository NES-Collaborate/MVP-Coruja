from flask import flash, redirect, url_for
from sqlalchemy.orm import aliased

from .extensions.database import db
from .models import Organ, organ_administrators


def get_organs_by_user_id(user_id: int):
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
