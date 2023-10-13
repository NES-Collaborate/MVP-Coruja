from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable


class Active(BaseTable):
    title = db.Column(db.String(255))
    description = db.Column(db.String)
    analysis_id = db.Column(db.Integer, db.ForeignKey("analysis.id"))

    analysis = db.relationship("Analysis", backref="actives", lazy=True)

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        analysis_id: Optional[int] = None,
    ):
        self.title = title
        self.description = description
        self.analysis_id = analysis_id


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
