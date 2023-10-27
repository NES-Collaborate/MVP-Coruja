import re
from typing import Any, Dict, List, Optional, overload

from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy.orm import aliased
from wtforms import ValidationError

from .extensions.database import db
from .models import (
    Active,
    ActiveScore,
    AdverseAction,
    AdverseActionScore,
    Analysis,
    AnalysisRisk,
    AnalysisVulnerability,
    Institution,
    Organ,
    Threat,
    Unit,
    User,
    Vulnerability,
    VulnerabilityCategory,
    VulnerabilitySubCategory,
    institution_administrators,
    institution_units,
    organ_administrators,
    organ_institutions,
    unit_analysis,
    units_administrators,
)


def form_to_dict(form: FlaskForm) -> Dict[Any, Any]:
    _new_form = {}
    for atributte in dir(form):
        if callable(getattr(form, atributte)) or atributte.startswith("_"):
            continue

        _new_form[atributte] = getattr(form, atributte)

    return _new_form


class UniqueData:
    def __init__(self, message: str):
        self.message = message

    def __call__(self, form, field):
        for _table in [Organ, Institution, User]:
            # Validação para campos únicos nas tabelas
            atributte = getattr(_table, field.name, None)
            if not atributte or not atributte.unique:
                continue

            # Se o campo do formulário não foi alterado na tabela
            if form.is_edit and getattr(form.obj, field.name) == field.data:
                return

            # Se o campo do formulário já está cadastrado nesta tabela
            if _table.query.filter_by(**{field.name: field.data}).first():
                raise ValidationError(self.message)


class DatabaseManager:
    def __init__(self):
        self.__db = db

    def get_organs(self, user_id: int) -> List[Organ]:
        """
        Obtém órgãos associados a um usuário com base em seu ID.

        Params:
            user_id (int): O ID do usuário a ser pesquisado.

        Return:
            list[Organ]: Uma lista de objetos Organ associados ao usuário especificado.
        """
        organ_admin_alias = aliased(organ_administrators)
        institution_admin_alias = aliased(institution_administrators)
        unit_admin_alias = aliased(units_administrators)

        # 1. Órgãos onde o user_id é um dos administradores
        query_1 = Organ.query.join(
            organ_admin_alias, Organ.id == organ_admin_alias.c.organ_id
        ).filter(organ_admin_alias.c.user_id == user_id)

        # 2. Órgãos relacionados às instituições onde o user_id é um dos administradores
        query_2 = (
            Organ.query.join(
                organ_institutions,  # Substitua pelo nome real da sua tabela associativa
                (organ_institutions.c.organ_id == Organ.id),
            )
            .join(
                institution_admin_alias,
                institution_admin_alias.c.institution_id
                == organ_institutions.c.institution_id,
            )
            .filter(institution_admin_alias.c.user_id == user_id)
        )

        # 3. Órgãos relacionados às unidades onde o user_id é um dos administradores
        query_3 = (
            Organ.query.join(
                organ_institutions,  # Substitua pelo nome real da sua tabela associativa
                (organ_institutions.c.organ_id == Organ.id),
            )
            .join(
                institution_units,  # Substitua pelo nome real da sua tabela associativa
                institution_units.c.institution_id
                == organ_institutions.c.institution_id,
            )
            .join(
                unit_admin_alias,
                unit_admin_alias.c.unit_id == institution_units.c.unit_id,
            )
            .filter(unit_admin_alias.c.user_id == user_id)
        )

        # Query Final:
        final_query = query_1.union(query_2).union(query_3)

        return final_query.all()

    def get_organ(
        self,
        organ_id: int,
        or_404: bool = True,
    ) -> Organ | None:
        # esta é outrra alteração aleatória eeeee

        """Obtém um orgão com base em seu ID.

        Args:
            organ_id (int): O ID do orgão.
            or_404 (bool, optional): Se True, caso não exista um orgão
                com o ID especificado, `abort(404)`. O padrão é True.

        Returns:
            Organ: O orgão com o ID especificado.
            None: Caso não exista um orgão com o ID especificado.
        """
        if or_404:
            message = "Orgão não encontrado"
            return Organ.query.filter_by(id=organ_id).first_or_404(message)

        return Organ.query.filter_by(id=organ_id).first()

    def update_organ(
        self,
        organ: Organ,
        form: Dict[str, Any],
    ) -> Organ:
        """Atualiza um orgão com base em seus dados

        Args:
            organ (Organ): O orgão a ser atualizado
            form (Dict[str, Any]): Os dados a serem atualizados

        Returns:
            Organ: O orgão atualizado
        """
        administrators: List[int] = form.pop("admin_ids", [])

        for key, value in form.items():
            setattr(organ, key, value)

        for administrator_id in administrators:
            administrator = self.get_user(administrator_id)
            organ.add_administrator(administrator)

        db.session.commit()

        return organ

    @overload
    def get_institutions(self, user_id: int) -> List[Institution]:
        """
        Obtém instituições associadas a um usuário com base em seu ID.

        Params:
            user_id (int): O ID do usuário a ser pesquisado.

        Return:
            list[Institution]: Uma lista de objetos Institution associados ao
                usuário especificado.
        """
        ...

    @overload
    def get_institutions(
        self,
        user_id: int,
        *,
        organ_id: int,
    ) -> List[Institution]:
        """
        Obtém instituições associadas a um usuário com base em seu ID
        e que estejam associados a um órgão.

        Params:
            user_id (int): O ID do usuário a ser pesquisado.
            organ_id (int): O ID do orgão a ser pesquisado.

        Return:
            list[Institution]: Uma lista de objetos Institution associados
                ao usuário e orgão especificado.
        """
        ...

    def get_institutions(
        self,
        user_id: int,
        *,
        organ_id: Optional[int] = None,
    ) -> List[Institution]:
        """Obtém instituições associadas a um usuario com base em seu ID e o órgão

        Args:
            user_id (int): O ID do usuário
            organ_id (Optional[int], optional): O ID do orgão. Defaults to None.

        Returns:
            List[Institution]: Uma lista de objetos Institution
        """
        user_institution_alias = aliased(institution_administrators)

        if organ_id is None:
            return (
                Institution.query.join(
                    user_institution_alias,
                    Institution.id == user_institution_alias.c.institution_id,
                )
                .filter(user_institution_alias.c.user_id == user_id)
                .all()
            )

        return (
            Institution.query.join(
                user_institution_alias,
                Institution.id == user_institution_alias.c.institution_id,
            )
            .filter(
                user_institution_alias.c.user_id == user_id,
                user_institution_alias.c.organ_id == organ_id,
            )
            .all()
        )

    def get_institution(
        self, institution_id: int, or_404: bool = True
    ) -> Institution | None:
        """Obtém uma instituição com base em seu ID.

        Args:
            institution_id (int): O ID da Instituição.
            or_404 (bool, optional): Se True, caso não exista uma Instituição
                com o ID especificado, `abort(404)`. O padrão é True.

        Returns:
            Institution: A instituição com o ID especificado.
            None: Caso não exista uma Instituição com o ID especificado.

        Raises:
            NotFoundError: Se a instituição não foi encontrada e `or_404=True`
        """
        institution = (
            Institution.query.filter_by(id=institution_id).first_or_404(
                "Instituição não encontrada"
            )
            if or_404
            else Institution.query.filter_by(id=institution_id).first()
        )
        return institution

    def update_institution(
        self,
        institution: Institution,
        form: Dict[str, Any],
    ) -> Institution:
        """Atualiza uma instituição com base em seus dados

        Args:
            institution (Institution): A instituição a ser atualizada
            form (Dict[str, Any]): Os dados a serem atualizados

        Returns:
            Institution: A instituição atualizada
        """
        administrators: List[int] = form.pop("admin_ids", [])

        for key, value in form.items():
            setattr(institution, key, value)

        for administrator_id in administrators:
            administrator = self.get_user(administrator_id)
            institution.add_administrator(administrator)

        db.session.commit()

        return institution

    def update_unit(
        self,
        unit: Unit,
        form: Dict[str, Any],
    ) -> Unit:
        """Atualiza uma unidade com base em seus dados

        Args:
            unit (Unit): A unidade a ser atualizada
            form (Dict[str, Any]): Os dados a serem atualizados

        Returns:
            Unit: A unidade atualizada
        """
        administrators: List[int] = form.pop("admin_ids", [])

        for key, value in form.items():
            setattr(unit, key, value)

        for administrator_id in administrators:
            administrator = self.get_user(administrator_id)
            unit.add_administrator(administrator)

        db.session.commit()

        return unit

    def get_analysis(
        self,
        analysis_id: int,
        or_404: bool = True,
    ) -> Analysis | None:
        """Obtém uma análise com base em seu ID.

        Args:
            analysis_id (int): O ID da análise.
            or_404 (bool, optional): Se True, caso não exista uma análise
                com o ID especificado, `abort(404)`. O padrão é True.

        Returns:
            Analysis: A análise com o ID especificado.
            None: Caso não exista uma análise com o ID especificado.
        """
        analysis = (
            Analysis.query.filter_by(id=analysis_id).first_or_404(
                "Análise não encontrada"
            )
            if or_404
            else Analysis.query.filter_by(id=analysis_id).first()
        )
        return analysis  # type: ignore

    def get_unit(
        self,
        unit_id: int,
        or_404: bool = True,
    ) -> Unit | None:
        """Obtém uma unidade com base em seu ID.

        Args:
            unit_id (int): O ID da unidade.
            or_404 (bool, optional): Se True, caso não exista uma unidade
                com o ID especificado, `abort(404)`. O padrão é True.

        Returns:
            Unit: A unidade com o ID especificado.
            None: Caso não exista uma unidade com o ID especificado.

        Raises:
            NotFoundError: Se a unidade não foi encontrada e `or_404=True`
        """

        unit = (
            Unit.query.filter_by(id=unit_id).first_or_404(
                "Unidade não encontrada"
            )
            if or_404
            else Unit.query.filter_by(id=unit_id).first()
        )
        return unit

    def get_user(self, user_id: int, or_404: bool = True) -> User:
        """Obtém um usuário com base em seu ID

        Args:
            user_id (int): O ID do usuário
            or_404 (bool, optional): Se True, caso não exista um usuário com
                o ID especificado, `abort(404)`. Defaults to True.

        Returns:
            User: O usuário com o ID especificado
        """
        user = (
            User.query.filter_by(id=user_id).first_or_404(
                "Usuário com o ID especificado ({}) não foi encontrado".format(
                    user_id
                )
            )
            if or_404
            else User.query.filter_by(id=user_id).first()
        )
        return user  # type: ignore

    def update_user(
        self,
        user: User,
        form: Dict[str, Any],
    ) -> User:
        """Atualiza um usuário com base em seus dados.

        Args:
            user (User): O usuário a ser atualizado.
            form (Dict[str, Any]): Os dados a serem atualizados.

        Returns:
            User: O usuário atualizado.
        """
        for key, value in form.items():
            setattr(user, key, value)

        db.session.commit()
        return user

    def add_user(self, **kwargs) -> User:
        kwargs["cpf"] = re.sub(r"\D", "", kwargs.get("cpf", ""))
        new_user = User(**kwargs)
        self.__db.session.add(new_user)
        self.__db.session.commit()
        return new_user

    def add_analysis(self, **kwargs) -> Analysis:
        """
        Cria uma nova análise e atribui administradores a ela.
        Relacionado à esta anaĺise cria Análise de Risco e Análise de Vulnerabilidade

        Args:
            description (str): A descrição da análise.
            administrators (List[int]): Lista de IDs dos administradores.

        Returns:
            Analysis: O objeto de análise recém-criado.
        """
        administrators = kwargs.pop("administrators", [])
        experts = kwargs.pop("experts", [])
        new_analysis = Analysis(description=kwargs.pop("description", None))

        for admin_id in administrators:
            admin = self.get_user(admin_id)
            new_analysis.add_administrator(admin, commit_changes=False)

        for expert_id in experts:
            expert = self.get_user(expert_id)
            new_analysis.add_expert(expert, commit_changes=False)

        self.__db.session.add(new_analysis)
        self.__db.session.commit()

        new_analysis_risk = AnalysisRisk(analysis_id=new_analysis.id)
        self.__db.session.add(new_analysis_risk)
        self.__db.session.commit()

        new_analysis_vulnerability = AnalysisVulnerability(
            analysis_id=new_analysis.id
        )
        self.__db.session.add(new_analysis_vulnerability)
        self.__db.session.commit()

        return new_analysis

    def update_analysis(
        self,
        analysis_id: int,
        description: str | None,
        administrators: List[int],
        experts: List[int],
    ) -> Analysis | None:
        """Atualiza os dados de uma análise com base em seu ID

        Args:
            analysis_id (int): ID da análise
            description (str): Nova descrição da análise
            administrators (List[int]): Nova lista de IDs dos administradores
            experts (List[int]): Nova lista de IDs dos especialistas

        Returns:
            Analysis: O objeto de análise atualizado
            None: Caso não exista uma analise com o ID especificado
        """
        analysis = self.get_analysis(analysis_id)
        if not analysis:
            return None
        analysis.description = description
        analysis.administrators = []
        analysis.experts = []

        for admin_id in administrators:
            admin = self.get_user(admin_id)
            analysis.add_administrator(admin, commit_changes=False)

        for expert_id in experts:
            expert = self.get_user(expert_id)
            analysis.add_expert(expert, commit_changes=False)

        db.session.commit()
        return analysis

    def get_actives_by_analysis(
        self,
        analysis: Analysis,
        with_average_scores: bool = True,
    ) -> List[Active]:
        """Obtém lista de ativos de uma determinada análise (ou seja, lista
        de ativos de uma análise de risco que está relacionada com a Análise
        especificada).

        Args:
            analysis (Analysis): Análise
            with_average_scores (bool, optional): Se True, inclui as médias
                dos scores dos ativos. Defaults to True.

        Returns:
            List[Active]: Lista de ativos.
        """
        analysis_risk = analysis.analysis_risk
        if not analysis_risk:
            return []

        actives = Active.query.filter_by(
            analysis_risk_id=analysis_risk.id
        ).all()

        if with_average_scores:
            for active in actives:
                active_scores: List[ActiveScore] = ActiveScore.query.filter_by(
                    active_id=active.id
                ).all()
                denominator = (
                    len(active_scores) if len(active_scores) > 0 else 1
                )
                active.average_substitutability = sum(
                    score.substitutability for score in active_scores
                ) / (denominator)
                active.average_replacement_cost = sum(
                    score.replacement_cost for score in active_scores
                ) / (denominator)
                active.average_essentiality = sum(
                    score.essentiality for score in active_scores
                ) / (denominator)
        return actives

    def add_organ(self, **kwargs) -> None:
        """Adiciona um órgão ao banco de dados e atribui administradores
        especificados a ele.

        Args:
            **kwargs (dict): Argumentos de palavra-chave contendo os atributos
                do órgão a ser adicionado e os IDs dos administradores.
        """
        administrators = kwargs.pop("administrators", [])
        organ = Organ(**kwargs)

        self.__db.session.add(organ)
        self.__db.session.commit()

        for administrator_id in administrators:
            administrator = self.get_user(administrator_id)
            organ.add_administrator(administrator)

    def add_institution(self, **kwargs) -> Institution:
        """Adiciona uma instituição ao banco de dados e atribui administradores
        especificados a ela.

        Args:
            **kwargs (dict): Argumentos de palavra-chave contendo os atributos
                da instituição a ser adicionada e os IDs dos administradores.
            administrators (List[int]): Lista de IDs dos administradores

        Returns:
            Institution: A instituição adicionada ao banco de dados.
        """

        administrators = kwargs.pop("administrators", [])
        institution = Institution(**kwargs)

        self.__db.session.add(institution)
        self.__db.session.commit()

        for administrator_id in administrators:
            administrator = self.get_user(administrator_id)
            institution.add_administrator(administrator, commit_changes=False)

        self.__db.session.commit()
        return institution

    def add_unit(self, **kwargs) -> Unit:
        """Adiciona uma unidade ao banco de dados e atribui administradores

        Args:
            **kwargs (dict): Argumentos de palavra-chave contendo os atributos
                definidos pelo formulário de edição

        Returns:
            Unit: A unidade adicionada ao banco de dados
        """
        administrators = kwargs.pop("administrators", [])
        unit = Unit(**kwargs)

        self.__db.session.add(unit)
        self.__db.session.commit()

        for administrator_id in administrators:
            administrator = self.get_user(administrator_id)
            unit.add_administrator(administrator)

        self.__db.session.commit()
        return unit

    def add_active(self, **kwargs) -> Active:
        """Adiciona um ativo ao banco de dados"""
        active = Active(**kwargs)

        self.__db.session.add(active)
        self.__db.session.commit()

        return active

    def add_threat(self, **kwargs) -> Threat:
        """Adiciona uma ameaça ao banco de dados"""
        threat = Threat(**kwargs)

        self.__db.session.add(threat)
        self.__db.session.commit()

        return threat

    def add_adverse_action(self, **kwargs) -> AdverseAction:
        """Adiciona uma ação adversa ao banco de dados"""

        adverse_action = AdverseAction(**kwargs)

        self.__db.session.add(adverse_action)
        self.__db.session.commit()

        return adverse_action

    def get_analysis_risk(
        self, analysis_risk_id: int, or_404: bool = True
    ) -> AnalysisRisk | None:
        """Obtém uma analise de risco por ID

        Args:
            analysis_risk_id (int): ID da analise
            or_404 (bool, optional): Se True, abort(404) caso não exista uma analise de
                risco com o ID especificado. Defaults to True

        Returns:
            AnalysisRisk: O objeto de analise
            None: Caso não exista uma analise de risco com o ID especificado

        Raises:
            NotFoundError: Se `or_404=True` e a analise de risco não foi encontrada
        """
        analysis_risk = (
            AnalysisRisk.query.filter_by(id=analysis_risk_id).first_or_404(
                "Análise de Risco não encontrada"
            )
            if or_404
            else AnalysisRisk.query.filter_by(id=analysis_risk_id).first()
        )

        return analysis_risk

    def get_threat(self, threat_id: int, or_404: bool = True) -> Threat | None:
        """Obtém uma ameaça por ID"""

        threat = (
            Threat.query.filter_by(id=threat_id).first_or_404(
                "Ameaça não encontrada"
            )
            if or_404
            else Threat.query.filter_by(id=threat_id).first()
        )

        return threat

    def get_adverse_action(
        self, adverse_action_id: int, or_404: bool = True
    ) -> AdverseAction | None:
        """Obtém uma ação adversa por ID"""

        adverse_action = (
            AdverseAction.query.filter_by(id=adverse_action_id).first_or_404(
                "Ação Adversa não encontrada"
            )
            if or_404
            else AdverseAction.query.filter_by(id=adverse_action_id).first()
        )

        return adverse_action

    def get_analysis_vulnerability(
        self, analysis_vulnerability_id: int, or_404: bool = True
    ) -> AnalysisVulnerability | None:
        """Obtém uma analise de vulnerabilidade por ID

        Args:
            analysis_vulnerability_id (int): ID da analise de vulnerabilidade
            or_404 (bool, optional): Se True, abort(404) caso não exista uma analise de vulnerabilidade com o ID especificado. Defaults to True

        Returns:
            AnalysisVulnerability: O objeto de analise de vulnerabilidade
            None: Caso não exista uma analise de vulnerabilidade com o ID especificado

        Raises:
            NotFoundError: Se `or_404=True` e a analise de vulnerabilidade não foi encontrada
        """
        analysis_vulnerability = (
            AnalysisVulnerability.query.filter_by(
                id=analysis_vulnerability_id
            ).first_or_404("Análise de Vulnerabilidade não encontrada")
            if or_404
            else AnalysisVulnerability.query.filter_by(
                id=analysis_vulnerability_id
            ).first()
        )
        return analysis_vulnerability

    def get_active(self, active_id: int, or_404: bool = True) -> Active | None:
        """Obtém um ativo por ID

        Args:
            active_id (int): ID do ativo
            or_404 (bool, optional): Se True, abort(404) caso não exista um ativo com o ID especificado. Defaults to True

        Returns:
            Active: O objeto do ativo
            None: Caso não exista um ativo com o ID especificado
        """
        active = (
            Active.query.filter_by(id=active_id).first_or_404(
                "Ativo não encontrado"
            )
            if or_404
            else Active.query.filter_by(id=active_id).first()
        )
        return active

    def get_adverse_actions(
        self,
        *,
        threat_id: int,
        user_id: int | None = None,
        with_scores: bool = True,
    ) -> List[Dict]:
        """Obtém uma lista de ações adversas

        Args:
            threat_id (int): ID da Ameaça com a qual está relacionadas as ações adversas
            with_scores (bool, optional): Se True, atribui scores. Padrão é True.
            user_id (int | None, optional): ID do usuário que atribuiu notas
                (Caso `with_scores=True`). Padrão é `flask_login.current_user`.

        Returns:
            List[AdverseAction]: A lista de ações adversas
        """
        user_id = user_id or current_user.id  # type: ignore [current_user isn't None]
        _adverse_actions = AdverseAction.query.filter_by(
            threat_id=threat_id
        ).all()
        _new_adverse_actions = []
        for adverse_action in _adverse_actions:
            adverse_action = adverse_action.as_dict()
            if with_scores:
                adverse_action_scores = AdverseActionScore.query.filter_by(
                    adverse_action_id=adverse_action["id"], user_id=user_id
                ).first()
                adverse_action["scores"] = (
                    adverse_action_scores.as_dict()
                    if adverse_action_scores
                    else {}
                )
            _new_adverse_actions.append(adverse_action)

        return _new_adverse_actions

    def add_vulnerability_category(self, name: str) -> None:
        """Adiciona uma nova categoria de vulnerabilidade

        Args:
            name (str): Nome da nova categoria de vulnerabilidade
        """

        vulnerability_category = VulnerabilityCategory(
            name=name, is_template=False
        )  # Adicionado is_template=False

        self.__db.session.add(vulnerability_category)
        self.__db.session.commit()

    def get_category(
        self,
        category_id: int,
        or_404: bool = True,
    ) -> VulnerabilityCategory | None:
        if or_404:
            message = "Categoria não encontrado"
            return VulnerabilityCategory.query.filter_by(
                id=category_id
            ).first_or_404(message)

        return VulnerabilityCategory.query.filter_by(id=category_id).first()

    def update_vulnerability_category(
        self,
        vulnerability_category: VulnerabilityCategory,
        form: Dict[str, Any],
    ) -> VulnerabilityCategory:
        """
        Atualiza uma categoria de vulnerabilidade com base nos dados fornecidos.

        Args:
            vulnerability_category (VulnerabilityCategory): A categoria de vulnerabilidade a ser atualizada.
            form (Dict[str, Any]): O dicionário contendo os campos a serem atualizados.

        Returns:
            VulnerabilityCategory: A categoria de vulnerabilidade atualizada.
        """
        for key, value in form.items():
            setattr(vulnerability_category, key, value)
        self.__db.session.commit()

        return vulnerability_category

    def add_vulnerability_subcategory(
        self, name: str, category_id: int
    ) -> None:
        """Adiciona uma nova categoria de vulnerabilidade

        Args:
            name (str): Nome da nova categoria de vulnerabilidade
        """

        vulnerability_subcategory = VulnerabilitySubCategory(
            name=name, is_template=False
        )
        vulnerability_subcategory.category_id = category_id
        self.__db.session.add(vulnerability_subcategory)
        self.__db.session.commit()

    def get_subcategory(
        self,
        subcategory_id: int,
        or_404: bool = True,
    ) -> VulnerabilitySubCategory | None:
        if or_404:
            message = "Subcategoria não encontrada"
            return VulnerabilitySubCategory.query.filter_by(
                id=subcategory_id
            ).first_or_404(message)

        return VulnerabilitySubCategory.query.filter_by(
            id=subcategory_id
        ).first()

    def update_vulnerability_subcategory(
        self,
        vulnerability_subcategory: VulnerabilitySubCategory,
        form: Dict[str, Any],
    ) -> VulnerabilitySubCategory:
        for key, value in form.items():
            setattr(vulnerability_subcategory, key, value)
        self.__db.session.commit()
        return vulnerability_subcategory

    def add_vulnerability(
        self,
        name: str,
        description: str,
        sub_category_id: int,
        is_template: bool = False,
    ) -> None:
        """Adiciona uma nova vulnerabilidade

        Args:
            name (str): Nome da nova vulnerabilidade
            description (str): Descrição da nova vulnerabilidade
            sub_category_id (int): ID da subcategoria à qual a vulnerabilidade pertence
            is_template (bool): Indica se a vulnerabilidade é um template
        """

        vulnerability = Vulnerability(
            name=name,
            description=description,
            is_template=is_template,
        )
        vulnerability.sub_category_id = sub_category_id
        self.__db.session.add(vulnerability)
        self.__db.session.commit()

    def get_vulnerability(
        self,
        vulnerability_id: int,
        or_404: bool = True,
    ) -> Vulnerability | None:
        """Obtém uma vulnerabilidade pelo seu ID

        Args:
            vulnerability_id (int): ID da vulnerabilidade
            or_404 (bool): Se True, lança um erro 404 se a vulnerabilidade não for encontrada
        """

        if or_404:
            message = "Vulnerabilidade não encontrada"
            return Vulnerability.query.filter_by(
                id=vulnerability_id
            ).first_or_404(message)

        return Vulnerability.query.filter_by(id=vulnerability_id).first()

    def update_vulnerability(
        self,
        vulnerability: Vulnerability,
        form: Dict[str, Any],
    ) -> Vulnerability:
        """Atualiza uma vulnerabilidade existente

        Args:
            vulnerability (Vulnerability): O objeto Vulnerability que será atualizado
            form (Dict[str, Any]): Dicionário contendo os novos valores para atualizar o objeto
        """

        for key, value in form.items():
            setattr(vulnerability, key, value)

        self.__db.session.commit()

        return vulnerability

    def get_institution_by_unit(self, unit_id: int) -> Institution | None:
        """Obtém uma instituição por unidade

        Args:
            unit_id (int): ID da unidade

        Returns:
            Institution | None: O objeto da instituição
        """
        institution_units_alias = aliased(institution_units)
        return (
            Institution.query.join(institution_units_alias)
            .filter(institution_units_alias.c.unit_id == unit_id)
            .first()
        )

    def get_unit_by_analysis(self, analysis_id: int) -> Unit | None:
        """Obtém uma unidade por análise

        Args:
            analysis_id (int): ID da análise

        Returns:
            Unit | None: O objeto da unidade ou None
        """
        unit_analysis_alias = aliased(unit_analysis)
        return (
            Unit.query.join(unit_analysis_alias).filter(
                unit_analysis_alias.c.analysis_id == analysis_id
            )
        ).first()

    def get_organ_by_institution(self, institution_id: int) -> Organ | None:
        organ_institutions_alias = aliased(organ_institutions)
        return (
            Organ.query.join(organ_institutions_alias)
            .filter(
                organ_institutions_alias.c.institution_id == institution_id
            )
            .first()
        )


database_manager = DatabaseManager()
