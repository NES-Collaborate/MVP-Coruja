from ..extensions.database import db

# Relacionamento de Permissões
permissions_roles = db.Table(
    "permissions_roles",
    db.Column("role_id", db.String, db.ForeignKey("role.id")),
    db.Column("permission_id", db.String, db.ForeignKey("permission.id")),
)

# Relacionamento de Orgãos
organ_administrators = db.Table(
    "organ_administrators",
    db.Column(
        "organ_id",
        db.Integer,
        db.ForeignKey("organ.id"),
        primary_key=True,
    ),
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
    ),
)

organ_institutions = db.Table(
    "organ_institutions",
    db.Column(
        "organ_id",
        db.Integer,
        db.ForeignKey("organ.id"),
        primary_key=True,
    ),
    db.Column(
        "institution_id",
        db.Integer,
        db.ForeignKey("institution.id"),
        primary_key=True,
    ),
)

# Relacionamento de Instituições
institution_administrators = db.Table(
    "institution_administrators",
    db.Column("institution_id", db.Integer, db.ForeignKey("institution.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

institution_units = db.Table(
    "institution_units",
    db.Column(
        "institution_id",
        db.Integer,
        db.ForeignKey("institution.id"),
        primary_key=True,
    ),
    db.Column(
        "unit_id",
        db.Integer,
        db.ForeignKey("unit.id"),
        primary_key=True,
    ),
)

# Relacionamento de Unidades
units_administrators = db.Table(
    "units_administrators",
    db.Column("unit_id", db.Integer, db.ForeignKey("unit.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

units_staff = db.Table(
    "units_staff",
    db.Column("unit_id", db.Integer, db.ForeignKey("unit.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

unit_analysis = db.Table(
    "unit_analysis",
    db.Column("unit_id", db.Integer, db.ForeignKey("unit.id")),
    db.Column("analysis_id", db.Integer, db.ForeignKey("analysis.id")),
)

# Relacionamento de Análises
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
