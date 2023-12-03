from typing import Optional

from ..extensions.database import db
from .configurations import BaseTable


class Permission(BaseTable):
    # "create", "read", "update", "delete"
    type = db.Column(db.String(255), nullable=False)
    # "organ", "unit", "user", "access_logs"
    object_type = db.Column(db.String(255), nullable=False)
    object_id = db.Column(db.Integer)

    def __init__(
        self,
        *,
        type: str,
        object_type: str,
        object_id: Optional[int] = None,
    ):
        """Permissão de acesso à funcionalidades gerais da aplicação

        Args:
            type (str): Tipo de permissão (`create`, `read`, `update`, `delete`)
            object_type (str): Tipo de objeto (`organ`, `unit`, `user`)
            object_id (Optional[int], optional): ID do objeto. Padrão é None.
        """
        self.type = type
        self.object_type = object_type
        self.object_id = object_id
