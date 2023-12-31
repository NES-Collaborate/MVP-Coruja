from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable
from .dangers import Threat


class Active(BaseTable):
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    analysis_risk_id = db.Column(db.Integer, db.ForeignKey("analysis_risk.id"))
    is_template = db.Column(db.Boolean, default=False)

    associated_threats = db.relationship(
        "Threat",
        foreign_keys=[Threat.active_id],
        backref=db.backref("active_threat", lazy=True),
        lazy=True,
        overlaps="associated_threats",
    )

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        analysis_risk_id: Optional[int] = None,
        is_template: Optional[bool] = False,
    ):
        self.title = title
        self.description = description
        self.analysis_risk_id = analysis_risk_id
        self.is_template = is_template

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}  # type: ignore

    def add_threat(self, threat: Threat):
        if not self.associated_threats:
            self.associated_threats = []
        self.associated_threats.append(threat)
        db.session.commit()


class ActiveScore(BaseTable):
    substitutability = db.Column(db.Integer, nullable=False, default=0)
    replacement_cost = db.Column(db.Integer, nullable=False, default=0)
    essentiality = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    active_id = db.Column(
        db.Integer, db.ForeignKey("active.id"), nullable=False
    )

    user = db.relationship("User", backref="acitve_scores", lazy=True)
    active = db.relationship("Active", backref="acitve_scores", lazy=True)

    def __init__(
        self,
        *,
        substitutability: int = 0,
        replacement_cost: int = 0,
        essentiality: int = 0,
        user_id: int,
        active_id: int,
    ):
        self.substitutability = substitutability
        self.replacement_cost = replacement_cost
        self.essentiality = essentiality
        self.user_id = user_id
        self.active_id = active_id

    def as_dict(self):
        return {
            "substitutability": self.substitutability,
            "replacement_cost": self.replacement_cost,
            "essentiality": self.essentiality,
        }
