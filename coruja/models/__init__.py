from datetime import datetime

from flask_login import current_user
from sqlalchemy import event

from ..extensions.database import db
from .actives import Active, ActiveScore
from .analysis import Analysis, AnalysisRisk, AnalysisVulnerability
from .configurations import AccessLog, BaseTable, Change
from .dangers import (
    AdverseAction,
    AdverseActionScore,
    Threat,
    Vulnerability,
    VulnerabilityCategory,
    VulnerabilityScore,
    VulnerabilitySubCategory,
)
from .institution import Institution, institution_administrators, institution_units
from .organs import Organ
from .relationships import (
    analytics_administrators,
    analytics_experts,
    organ_administrators,
    organ_institutions,
    permissions_roles,
    unit_analysis,
    units_administrators,
    units_staff,
    vulnerability_categories,
)
from .units import Unit
from .users import Permission, Role, User

__all__ = [
    "User",
    "Unit",
    "Role",
    "Organ",
    "Active",
    "Threat",
    "Analysis",
    "AccessLog",
    "Permission",
    "units_staff",
    "Institution",
    "ActiveScore",
    "AnalysisRisk",
    "Vulnerability",
    "unit_analysis",
    "AdverseAction",
    "analytics_experts",
    "institution_units",
    "permissions_roles",
    "organ_institutions",
    "AdverseActionScore",
    "VulnerabilityScore",
    "units_administrators",
    "organ_administrators",
    "AnalysisVulnerability",
    "VulnerabilityCategory",
    "vulnerability_categories",
    "VulnerabilitySubCategory",
    "analytics_administrators",
    "institution_administrators",
    "Change",
]


def serialize(model_instance):
    serialized_data = {}
    for c in model_instance.__table__.columns:
        value = getattr(model_instance, c.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        serialized_data[c.name] = value
    return serialized_data


def capture_initial_state(target, query_context):
    target._original_state = serialize(target)


def capture_and_compare_changes(session, flush_context):
    for obj in session.dirty:
        if not hasattr(obj, "_original_state"):
            continue

        current_state = serialize(obj)
        original_state = obj._original_state
        if original_state != current_state:
            obj.updated_at = datetime.now()
            current_state["updated_at"] = obj.updated_at
            change = Change(
                object_old=original_state,
                object_new=current_state,
                user_id=current_user.id,  # type: ignore
                object_type=obj.__class__.__name__,
            )
            session.add(change)


for name, value in locals().copy().items():
    if (
        isinstance(value, type)
        and issubclass(value, BaseTable)
        and name not in ("BaseTable", "Change", "AccessLog")
    ):
        event.listen(value, "load", capture_initial_state)

event.listen(db.session, "after_flush", capture_and_compare_changes)
