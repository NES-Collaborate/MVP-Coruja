from typing import Optional

from ..extensions.database import db
from .analysis import Analysis
from .configurations import BaseTable
from .relationships import unit_analysis, units_administrators, units_staff
from .users import User


class Unit(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255))
    description = db.Column(db.String(255))
    is_template = db.Column(db.Boolean, default=False)

    analyses = db.relationship(
        "Analysis",
        secondary=unit_analysis,
        backref=db.backref("units", lazy="dynamic"),
    )
    administrators = db.relationship(
        "User",
        secondary=units_administrators,
        backref=db.backref("units_administered", lazy="dynamic"),
    )
    staff = db.relationship(
        "User",
        secondary=units_staff,
        backref=db.backref("units_staffed", lazy="dynamic"),
    )

    def __init__(
        self,
        *,
        name: str,
        address: str,
        description: Optional[str] = None,
        is_template: Optional[bool] = False
    ) -> None:
        self.name = name
        self.address = address
        self.description = description
        self.is_template = is_template

    def add_administrator(self, user: User):
        """Adiciona um administrador a uma unidade

        Args:
            user (User): Usuário a ser adicionado
        """
        permissions = self.create_permissions()
        if not self.administrators:
            self.administrators = []

        self.administrators.append(user)
        for permission in permissions:
            user.add_permission(permission)

    def add_analysis(self, analysis: Analysis):
        """Adiciona uma análise a uma unidade

        Args:
            analysis (Analysis): Análise a ser adicionada
        """
        if not self.analyses:
            self.analyses = []

        self.analyses.append(analysis)

        db.session.commit()
