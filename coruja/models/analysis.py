from typing import Optional

from ..extensions.database import db
from .actives import Active
from .configurations import BaseTable

analytics_administrators = db.Table(
    "analytics_administrators",
    db.Column("analysis_id", db.Integer, db.ForeignKey("analysis.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

analytics_staff = db.Table(
    "analytics_staff",
    db.Column("analysis_id", db.Integer, db.ForeignKey("analysis.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class Analysis(BaseTable):
    description = db.Column(db.String)

    administrators = db.relationship(
        "User",
        secondary=analytics_administrators,
        backref=db.backref("analytics_administered", lazy="dynamic"),
    )
    staff = db.relationship(
        "User",
        secondary=analytics_staff,
        backref=db.backref("analytics_staffed", lazy="dynamic"),
    )

    analysis_risk = db.relationship(
        "AnalysisRisk",
        backref="analysis",
        lazy=True,
    )
    analysis_vulnerability = db.relationship(
        "AnalysisVulnerability",
        backref="analysis",
        lazy=True,
    )

    def __init__(self, *, description: Optional[str] = None):
        self.description = description


class AnalysisRisk(BaseTable):
    analysis_id = db.Column(db.Integer, db.ForeignKey("analysis.id"))

    def __init__(self, analysis_id):
        self.analysis_id = analysis_id

    associated_actives = db.relationship(
        "Active",
        foreign_keys=[Active.analysis_risk_id],
        backref=db.backref("analysis_risk", lazy=True),
        lazy=True,
        overlaps="associated_actives",
    )


vulnerability_categories = db.Table(
    "vulnerability_categories",
    db.Column(
        "analysis_vulnerability_id",
        db.Integer,
        db.ForeignKey("analysis_vulnerability.id"),
    ),
    db.Column(
        "vulnerability_category_id",
        db.Integer,
        db.ForeignKey("vulnerability_category.id"),
    ),
)


class AnalysisVulnerability(BaseTable):
    analysis_id = db.Column(db.Integer, db.ForeignKey("analysis.id"))
    vulnerability_categories = db.relationship(
        "VulnerabilityCategory",
        secondary=vulnerability_categories,
        backref=db.backref("analysis_vulnerabilities", lazy="dynamic"),
    )
