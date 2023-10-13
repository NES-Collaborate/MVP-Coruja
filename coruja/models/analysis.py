from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable

analytics_administrators = db.Table(
    "analytics_administrators",
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

    def __init__(self, *, description: Optional[str] = None):
        self.description = description
