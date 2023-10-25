from functools import wraps
from typing import Any, Callable, Mapping, Optional

from flask import abort
from flask_login import current_user
from werkzeug.local import LocalProxy

from ..models import User
from ..utils import database_manager


def is_object_administrator(obj: object, user: User | LocalProxy) -> bool:
    """Verifica se o usuário é um administrador do objeto

    Args:
        obj (object): O objeto (deve ter atributo `administrators` como `List[User]`)
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário é um administrador do objeto
    """
    return any(user.id == admin.id for admin in obj.administrators)  # type: ignore


def can_access_organ(organ_id: int, user: User) -> bool:
    """Verifica se o usuário tem permissão para acessar o órgão

    Args:
        organ_id (int): ID do órgão
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário tem permissão para acessar o órgão

    Raises:
        NotFoundError: Se o órgão não foi encontrado
    """
    organ = database_manager.get_organ(organ_id)
    if organ is None:
        abort(404, message="Órgão não encontrado")
    can_access = database_manager.is_organ_administrator(user)
    return can_access or is_object_administrator(organ, user)


def can_access_institution(
    institution_id: int, user: User | LocalProxy
) -> bool:
    """Verifica se o usuário tem permissão para acessar a instituição

    Args:
        institution_id (int): ID da instituição
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário tem permissão para acessar a instituição
    """
    institution = database_manager.get_institution(institution_id)
    can_access = is_object_administrator(institution, user)
    return can_access or can_access_organ(institution.organ_id, user)  # type: ignore [institution isn't None]


def can_access_unit(unit_id: int, user: User) -> bool:
    """Verifica se o usuário tem permissão para acessar a unidade

    Args:
        unit_id (int): ID da unidade
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário tem permissão para acessar a unidade
    """
    unit = database_manager.get_unit(unit_id)
    can_access = is_object_administrator(unit, user)
    return can_access or can_access_institution(unit.institution_id, user)  # type: ignore [unit isn't None]


def can_access_analysis(analysis_id: int, user: User) -> bool:
    """Verifica se o usuário tem permissão para acessar a analise

    Args:
        analysis_id (int): ID da analise
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário tem permissão para acessar a analise
    """

    analysis = database_manager.get_analysis(analysis_id)
    can_access = is_object_administrator(analysis, user)
    return can_access or can_access_unit(analysis.unit_id, user)  # type: ignore [analysis isn't None]


def can_access_analysis_risk(analysis_risk_id: int, user: User) -> bool:
    """Verifica se usuário especificado tem permissão para acessar a analise

    Args:
        analysis_risk_id (int): ID da analise
        user (User): Usuário a ser verificado

    Returns:
        bool: Se usuário especificado tem permissão para acessar a analise
    """
    analysis_risk = database_manager.get_analysis(analysis_risk_id)
    can_access = is_object_administrator(analysis_risk, user)
    return can_access or can_access_analysis(analysis_risk.analysis_id, user)  # type: ignore [analysis_risk isn't None]


def can_access_analysis_vulnerability(
    analysis_vulnerability_id: int, user: User
) -> bool:
    """Verifica se o usuário tem permissão para acessar a vulnerabilidade

    Args:
        analysis_vulnerability_id (int): ID da vulnerabilidade
        user (User): Usuário a ser verificado

    Returns:
        bool: Se o usuário tem permissão para acessar a vulnerabilidade
    """
    analysis_vulnerability = database_manager.get_analysis_vulnerability(
        analysis_vulnerability_id
    )
    can_access = is_object_administrator(analysis_vulnerability, user)
    return can_access or can_access_analysis(analysis_vulnerability.analysis_id, user)  # type: ignore [analysis_vulnerability isn't None]


object_map: Mapping[str, Callable] = {
    "organ": can_access_organ,
    "institution": can_access_institution,
    "unit": can_access_unit,
    "analysis": can_access_analysis,
    "analysis_risk": can_access_analysis_risk,
    "analysis_vulnerability": can_access_analysis_vulnerability,
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

    Returns:
        Callable: Funcionalidade modificada

    Raises:
        KeyError: Caso o ID do objeto não seja encontrado entre as `kwargs`
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

            ids = [kwargs[_id] for _id in kwargs if _id.endswith("_id")]
            if not ids:
                raise KeyError("ID do objeto não encontrado")
            obj_id = ids[0]
            can_access = obj_class(obj_id, user)  # type: ignore
            if can_access:
                return function(*args, **kwargs)
            else:
                abort(403, message)

        return wrapper

    return decorator
