from functools import wraps
from typing import Callable, Mapping, Optional

from flask import abort
from flask_login import current_user

from ..models import Analysis, User
from ..utils import database_manager


def can_access_organ(organ_id: int, user: User) -> bool:
    """Verifica se o usuário tem permissão para acessar o órgão

    Args:
        organ_id (int): ID do órgão
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário tem permissão para acessar o órgão
    """
    organ = database_manager.get_organ_by_id(organ_id)
    can_access = database_manager.is_organ_administrator(user)
    if can_access:
        return can_access
    is_organ_admin = any(user.id == admin.id for admin in organ.administrators)
    return is_organ_admin


def can_access_institution(institution_id: int, user: User) -> bool:
    """Verifica se o usuário tem permissão para acessar a instituição

    Args:
        institution_id (int): ID da instituição
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário tem permissão para acessar a instituição
    """
    # TODO: Cabe a ser implementado por quem for cuidar de instituição
    #   deve verificar tanto se o usuário é um ados administradores, como
    #   deve verificar se o usuário can_access_organ
    institution: "Institution" = ...
    can_access = ...
    if can_access:
        return can_access
    can_access_father = can_access_organ(institution.organ_id, user)
    return can_access_father  # type: ignore


def can_access_unit(unit_id: int, user: User) -> bool:
    """Verifica se o usuário tem permissão para acessar a unidade

    Args:
        unit_id (int): ID da unidade
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário tem permissão para acessar a unidade
    """
    # TODO: Cabe a ser implementado por quem for cuidar de unidade
    #   deve verificar tanto se o usuário é um ados administradores, como
    #   deve verificar se o usuário can_access_institution (pai)

    unit: "Unit" = ...
    can_access = ...
    if can_access:
        return can_access
    can_access_father = can_access_institution(unit.institution_id, user)
    return can_access_father


def can_access_analysis(analysis_id: int, user: User) -> bool:
    """Verifica se o usuário tem permissão para acessar a analise

    Args:
        analysis_id (int): ID da analise
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário tem permissão para acessar a analise
    """
    # TODO: Cabe a ser implementado por quem for cuidar de analise
    #   deve verificar tanto se o usuário é um ados administradores, como
    #   deve verificar se o usuário can_access_unit (pai)

    analysis: "Analysis" = ...
    can_access = ...
    if can_access:
        return can_access
    can_access_father = can_access_unit(analysis.unit_id, user)
    return can_access_father


def can_access_analysis_risk(analysis_risk_id: int, user: User) -> bool:
    """Verifica se usuário especificado tem permissão para acessar a analise

    Args:
        analysis_risk_id (int): ID da analise
        user (User): Usuário a ser verificado

    Returns:
        bool: Se usuário especificado tem permissão para acessar a analise
    """
    analysis_risk: "AnalysisRisk" = ...
    can_access = ...
    if can_access:
        return can_access
    can_access_father = can_access_analysis(analysis_risk.analysis_id, user)
    return can_access_father


object_map: Mapping[str, Callable] = {
    "organ": can_access_organ,
    "instituition": can_access_institution,
    "unit": can_access_unit,
    "analysis": can_access_analysis,
    "analysis_risk": can_access_analysis_risk,
    # TODO: Adicionar mais objetos
}


def proxy_access(
    *,
    kind_object: str,
    kind_access: str,
    message: Optional[str] = None,
    user: Optional[User] = None,
) -> Callable:
    """Verifica se o usuário tem permissão para acessar o objeto correspondente

    Args:
        function (Callable): Funcionalidade
        kind_object (str): Tipo do objeto. Ex: `organ`, `instituition`, etc.
            Em caso de dúvidas, consulte `object_map`.
        kind_access (str): Tipo de acesso. Ex: `read`, `write`, etc.
        message (Optional[str], optional): Mensagem que deve ser exibida caso
            o usuário não tenha permissão. Defaults to None (mensagem padrão).
        user (Optional[User], optional): Usuário a ser verificado. Defaults to
            None (`flask_login.current_user`).

    Returns:
        Callable: Funcionalidade modificada
    """
    # TODO: implementar os diferentes tipos de access
    message = (
        f"Você não possui permissão {kind_access!r} para o objeto {kind_object!r}"
        or message
    )

    user = user or current_user  # type: ignore

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args, **kwargs):
            obj_class = object_map.get(kind_object)
            if obj_class is None:
                abort(403, message)

            obj_id = args[0]
            can_access = obj_class(obj_id, user)  # type: ignore
            if can_access:
                return function(*args, **kwargs)
            else:
                abort(403, message)

        return wrapper

    return decorator
