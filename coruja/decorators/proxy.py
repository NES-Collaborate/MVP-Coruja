from functools import wraps
from typing import Callable, Mapping, Optional

from flask import abort
from flask_login import AnonymousUserMixin, current_user
from werkzeug.local import LocalProxy

from ..models import User
from ..utils import database_manager


def organ_access(
    organ_id: int, user: User | LocalProxy, kind_access: str
) -> bool:
    if kind_access in ("read", "update") and not organ_id:
        return False

    user_permissions = getattr(user, "permissions")

    return any(
        permission.type == kind_access
        and permission.object_id == organ_id
        and permission.object_type == "organ"
        for permission in user_permissions
    ) or (
        organ_id
        and any(
            [
                institution_access(
                    institution.id, user, kind_access, True
                )
            ]
            for institution in database_manager.get_organ(
                organ_id
            ).institutions
        )
    )


def institution_access(
    institution_id: int,
    user: User | LocalProxy,
    kind_access: str,
    from_organ=False,
) -> bool:
    if (
        kind_access in ("read", "update")
        and not institution_id
    ):
        return False

    user_permissions = getattr(user, "permissions")
    organ = database_manager.get_organ_by_institution(
        institution_id
    )

    return (
        any(
            permission.type == kind_access
            and permission.object_id == institution_id
            and permission.object_type == "instituition"
            for permission in user_permissions
        )
        or (
            institution_id
            and any(
                [
                    unit_access(
                        unit.id, user, kind_access, True
                    )
                ]
                for unit in database_manager.get_institution(
                    institution_id
                ).units
            )
        )
        or (
            not from_organ
            and organ_access(
                getattr(organ, "id"), user, kind_access
            )
        )
    )


def unit_access(
    unit_id: int,
    user: User | LocalProxy,
    kind_access: str,
    from_institution=False,
) -> bool:
    user_permissions = getattr(user, "permissions")
    institution = database_manager.get_institution_by_unit(
        unit_id
    )

    return (
        any(
            permission.type == kind_access
            and permission.object_id == unit_id
            and permission.object_type == "unit"
            for permission in user_permissions
        )
        or (
            unit_id
            and any(
                [
                    analysis_access(
                        analysis.id, user, kind_access, True
                    )
                ]
                for analysis in database_manager.get_unit(
                    unit_id
                ).analyses
            )
        )
        or (
            not from_institution
            and institution_access(
                getattr(institution, "id"),
                user,
                kind_access,
            )
        )
    )


def analysis_access(
    analysis_id: int,
    user: User | LocalProxy,
    kind_access: str,
    from_unit=False,
) -> bool:
    user_permissions = getattr(user, "permissions")
    unit = database_manager.get_unit_by_analysis(
        analysis_id
    )

    return any(
        permission.type == kind_access
        and permission.object_id == analysis_id
        and permission.object_type == "analysis"
        for permission in user_permissions
    ) or (
        not from_unit
        and unit_access(
            getattr(unit, "id"), user, kind_access
        )
    )


def analysis_risk_access(
    analysis_risk_id: int, user: User | LocalProxy, kind_access: str
) -> bool:
    analysis_risk = database_manager.get_analysis_risk(analysis_risk_id)
    analysis_id = getattr(analysis_risk, "analysis_id")

    return analysis_access(analysis_id, user, kind_access)


def active_access(
    active_id: int, user: User | LocalProxy, kind_access: str
) -> bool:
    active = database_manager.get_active(active_id)
    analysis_risk_id = getattr(active, "analysis_risk_id")

    return analysis_risk_access(analysis_risk_id, user, kind_access)


def threat_acess(
    threat_id: int, user: User | LocalProxy, kind_access: str
) -> bool:
    threat = database_manager.get_threat(threat_id)
    active_id = getattr(threat, "active_id")

    return active_access(active_id, user, kind_access)


def adverse_action_access(
    adverse_action_id: int, user: User | LocalProxy, kind_access: str
) -> bool:
    adverse_action = database_manager.get_adverse_action(adverse_action_id)
    threat_id = getattr(adverse_action, "threat_id")

    return threat_access(threat_id, user, kind_access)


def user_access(
    user_id: int | None, user: User | LocalProxy, kind_access: str
) -> bool:
    user_permissions = getattr(user, "permissions")
    user_id = None  # esta linha está aqui por causa de um bug
    return any(
        permission.type == kind_access
        and permission.object_id == user_id
        and permission.object_type == "user"
        for permission in user_permissions
    )


def admin_access(
    object_id: None, user: User | LocalProxy, kind_access: str
) -> bool:
    if isinstance(user, AnonymousUserMixin):
        return False
    user_permissions = getattr(user, "permissions")
    object_id = None
    return any(
        permission.type == kind_access
        and permission.object_id == object_id
        and permission.object_type == "admin"
        for permission in user_permissions
    )


object_map: Mapping[str, Callable] = {
    "organ": organ_access,
    "institution": institution_access,
    "unit": unit_access,
    "analysis": analysis_access,
    "analysis_risk": analysis_risk_access,
    "active": active_access,
    "threat": threat_access,
    "adverse_action": adverse_action_access,
    "user": user_access,
    "admin": admin_access,
}

translate_kind = {
    "organ": "órgão",
    "institution": "instituição",
    "unit": "unidade",
    "analysis": "análise",
    "analysis_risk": "análise de risco",
    "active": "ativo",
    "threat": "ameaça",
    "adverse_action": "ação adversa",
    "user": "usuário",
    "read": "acessar",
    "write": "escrita",
    "create": "criação",
    "update": "atualização",
    "delete": "exclusão",
    "admin": "administração",
}


def proxy_access(
    *,
    kind_object: str,
    kind_access: str,
    message: Optional[str] = None,
    user: Optional[User] = None,
    has_obj_id: bool = True,
) -> Callable:
    """Verifica se o usuário tem permissão para acessar o objeto correspondente

    O ID do objeto deve algum argumento que termine com `_id`, ou seja, sua rota
    fica parecida com isto:


    ```
    @bp.route("/<int:example_id>")
    @proxy_access(kind_object="example", kind_access="read")
    def get_organ(example_id: int):
        ...
    ```

    Args:
        function (Callable): Funcionalidade
        kind_object (str): Tipo do objeto. Ex: `organ`, `instituition`, etc.
            Em caso de dúvidas, consulte `object_map`.
        kind_access (str): Tipo de acesso. Ex: `read`, `write`, etc.
        message (Optional[str], optional): Mensagem que deve ser exibida caso
            o usuário não tenha permissão. Defaults to None (mensagem padrão).
        user (Optional[User], optional): Usuário a ser verificado. Defaults to
            None (`flask_login.current_user`).
        has_obj_id (bool, optional): Se `True`, o ID do objeto será verificado.

    Returns:
        Callable: Funcionalidade modificada

    Raises:
        KeyError: Caso o ID do objeto não seja encontrado entre as `kwargs`
    """
    if not message:
        message = (
            f"Você não possui permissão para {translate_kind[kind_access]}"
            f" este/esta {translate_kind[kind_object]} no momento"
        )

    user = user or current_user  # type: ignore

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args, **kwargs):
            obj_class = object_map.get(kind_object)
            if obj_class is None:
                abort(403, message)

            ids = [kwargs[_id] for _id in kwargs if _id.endswith("_id")]
            if not ids and kind_access != "create" and has_obj_id:
                raise KeyError("ID do objeto não encontrado")
            obj_id = ids[0] if ids else None
            can_access = obj_class(obj_id, user, kind_access)  # type: ignore
            if can_access:
                return function(*args, **kwargs)
            else:
                abort(403, message)

        return wrapper

    return decorator


def proxy_access_function(
    kind_object: str,
    kind_access: str,
    user: Optional[User] = None,
    object_id: Optional[int] = None,
):
    user = user or current_user  # type: ignore

    func = object_map.get(kind_object, lambda x, y, z: False)
    return func(object_id, user, kind_access)  # type: ignore
