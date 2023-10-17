from typing import Optional

from ..extensions.database import db
from .actives import Active
from .configurations import BaseTable
from .users import User

analytics_administrators = db.Table(
    "analytics_administrators",
    db.Column("analysis_id", db.Integer, db.ForeignKey("analysis.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

analytics_experts = db.Table(
    "analytics_experts",
    db.Column("analysis_id", db.Integer, db.ForeignKey("analysis.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)


class Analysis(BaseTable):
    description = db.Column(db.String)
    is_template = db.Column(db.Boolean, default=False)

    administrators = db.relationship(
        "User",
        secondary=analytics_administrators,
        backref=db.backref("analytics_administered", lazy="dynamic"),
    )
    experts = db.relationship(
        "User",
        secondary=analytics_experts,
        backref=db.backref("analytics_experted", lazy="dynamic"),
    )

    analysis_risk = db.relationship(
        "AnalysisRisk",
        backref="analysis",
        uselist=False,
        lazy=True,
    )
    analysis_vulnerability = db.relationship(
        "AnalysisVulnerability",
        backref="analysis",
        uselist=False,
        lazy=True,
    )

    def __init__(
        self,
        *,
        description: Optional[str] = None,
        is_template: Optional[bool] = False
    ):
        self.description = description
        self.is_template = is_template

    def add_administrator(
        self, user: User, commit_changes: bool = True
    ) -> None:
        """Adiciona um administrador para a analise

        Args:
            user (User): usuário a ser adicionado
            commit_changes (bool, optional): Se True, salva as alterações no banco.
                Defaults to True.
        """
        if not self.administrators:
            self.administrators = []

        self.administrators.append(user)
        if commit_changes:
            db.session.commit()


class AnalysisRisk(BaseTable):
    analysis_id = db.Column(db.Integer, db.ForeignKey("analysis.id"))
    is_template = db.Column(db.Boolean, default=False)

    associated_actives = db.relationship(
        "Active",
        foreign_keys=[Active.analysis_risk_id],
        backref=db.backref("analysis_risk", lazy=True),
        lazy=True,
        overlaps="associated_actives",
    )

    def __init__(self, analysis_id: int, is_template: Optional[bool] = False):
        self.analysis_id = analysis_id
        self.is_template = is_template


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
