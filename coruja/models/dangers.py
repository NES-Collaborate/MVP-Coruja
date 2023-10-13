from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable


class Threat(BaseTable):
    title = db.Column(db.String(255))
    description = db.Column(db.String)
    active_id = db.Column(db.Integer, db.ForeignKey("active.id"))

    active = db.relationship("Active", backref="threats", lazy=True)

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        active_id: Optional[int] = None,
    ):
        self.title = title
        self.description = description
        self.active_id = active_id


class AdverseAction(BaseTable):
    title = db.Column(db.String(255))
    description = db.Column(db.String)
    threat_id = db.Column(db.Integer, db.ForeignKey("threat.id"))

    threat = db.relationship("Threat", backref="adverse_actions", lazy=True)

    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        threat_id: Optional[int] = None,
    ):
        self.title = title
        self.description = description
        self.threat_id = threat_id


class AdverseActionScore(BaseTable):
    motivation = db.Column(db.Integer, default=0)
    capacity = db.Column(db.Integer, default=0)
    accessibility = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    adverse_action_id = db.Column(
        db.Integer,
        db.ForeignKey("adverse_action.id"),
        nullable=False,
    )

    user = db.relationship("User", backref="adverse_actions_scores", lazy=True)
    adverse_action = db.relationship(
        "AdverseAction",
        backref="adverse_actions_scores",
        lazy=True,
    )

    def __init__(
        self,
        *,
        motivation: Optional[int] = 0,
        capacity: Optional[int] = 0,
        accessibility: Optional[int] = 0,
        user_id: int,
        adverse_action_id: int,
    ):
        self.motivation = motivation
        self.capacity = capacity
        self.accessibility = accessibility
        self.user_id = user_id
        self.adverse_action_id = adverse_action_id


class VulnerabilityCategory(BaseTable):
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, *, name: str):
        self.name = name


class VulnerabilitySubCategory(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("vulnerability_category.id"),
    )

    category = db.relationship(
        "VulnerabilityCategory",
        backref="vulnerability_sub_categories",
        lazy=True,
    )

    def __init__(self, *, name: str, category_id: Optional[int] = None):
        self.name = name
        self.category_id = category_id


class Vulnerability(BaseTable):
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String)
    sub_category_id = db.Column(
        db.Integer,
        db.ForeignKey("vulnerability_sub_category.id"),
    )

    sub_category = db.relationship(
        "VulnerabilitySubCategory",
        backref="vulnerabilities",
        lazy=True,
    )

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        sub_category_id: Optional[int] = None,
    ):
        self.name = name
        self.description = description
        self.sub_category_id = sub_category_id


class VulnerabilityScore(BaseTable):
    score = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    vulnerability_id = db.Column(
        db.Integer,
        db.ForeignKey("vulnerability.id"),
        nullable=False,
    )

    user = db.relationship("User", backref="vulnerability_scores", lazy=True)
    vulnerability = db.relationship(
        "Vulnerability",
        backref="vulnerability_scores",
        lazy=True,
    )

    def __init__(self, *, score: int = 0, user_id: int, vulnerability_id: int):
        self.score = score
        self.user_id = user_id
        self.vulnerability_id = vulnerability_id
