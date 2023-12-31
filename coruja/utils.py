import re
from typing import Any, Dict, List, Optional, Tuple, overload

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
    VulnerabilityScore,
    VulnerabilitySubCategory,
    analytics_administrators,
    analytics_experts,
    institution_administrators,
    institution_units,
    organ_administrators,
    organ_institutions,
    unit_analysis,
    units_administrators,
)


def form_to_dict(form: FlaskForm) -> Dict[Any, Any]:
    _new_form = {}
    for attribute in dir(form):
        if callable(getattr(form, attribute)) or attribute.startswith("_"):
            continue

        _new_form[attribute] = getattr(form, attribute)

    return _new_form


def parse_nullables(cls_model: Any, form: FlaskForm):
    is_dunder = lambda attribute: not attribute.startswith("_")
    fields = filter(is_dunder, dir(form))

    for field_form in fields:
        _field_form = getattr(form, field_form, None)
        field_table = getattr(cls_model, field_form, None)

        if not _field_form or not field_table:
            continue

        if field_table.nullable and _field_form.data == "":
            _field_form.data = None

    return form


class UniqueData:
    def __init__(self, message: str):
        self.message = message

    def __call__(self, form, field):
        for _table in [Organ, Institution, User]:
            # Validação para campos únicos nas tabelas
            attribute = getattr(_table, field.name, None)
            if not attribute or not attribute.unique:
                continue

            # # Se o campo do formulário estiver vazio
            # if field.nullable and field.data == "":
            #     field.data = None

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
            organ_admin_alias,
            Organ.id == organ_admin_alias.c.organ_id,
        ).filter(organ_admin_alias.c.user_id == user_id)

        # 2. Órgãos relacionados às instituições onde o user_id é um dos administradores
        query_2 = (
            Organ.query.join(
                organ_institutions,
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
                organ_institutions,
                (organ_institutions.c.organ_id == Organ.id),
            )
            .join(
                institution_units,
                institution_units.c.institution_id
                == organ_institutions.c.institution_id,
            )
            .join(
                unit_admin_alias,
                unit_admin_alias.c.unit_id == institution_units.c.unit_id,
            )
            .filter(unit_admin_alias.c.user_id == user_id)
        )

        # 4. Órgãos relacionados às análises onde o user_id é um dos administradores
        query_4 = (
            Organ.query.join(
                organ_institutions,
                (organ_institutions.c.organ_id == Organ.id),
            )
            .join(
                institution_units,
                institution_units.c.institution_id
                == organ_institutions.c.institution_id,
            )
            .join(
                unit_analysis,
                unit_analysis.c.unit_id == institution_units.c.unit_id,
            )
            .join(
                analytics_administrators,
                analytics_administrators.c.analysis_id
                == unit_analysis.c.analysis_id,
            )
            .filter(analytics_administrators.c.user_id == user_id)
        )

        # 5. Órgãos relacionados às análises onde o user_id é um dos experts
        query_5 = (
            Organ.query.join(
                organ_institutions,
                (organ_institutions.c.organ_id == Organ.id),
            )
            .join(
                institution_units,
                institution_units.c.institution_id
                == organ_institutions.c.institution_id,
            )
            .join(
                unit_analysis,
                unit_analysis.c.unit_id == institution_units.c.unit_id,
            )
            .join(
                analytics_experts,
                analytics_experts.c.analysis_id == unit_analysis.c.analysis_id,
            )
            .filter(analytics_experts.c.user_id == user_id)
        )

        # Query Final:
        final_query = (
            query_1.union(query_2).union(query_3).union(query_4).union(query_5)
        )

        return final_query.all()

    def get_organ(
        self,
        organ_id: int,
        or_404: bool = True,
    ) -> Organ | None:
        # esta é outra alteração aleatória eeeee

        """Obtém um órgão com base em seu ID.

        Args:
            organ_id (int): O ID do órgão.
            or_404 (bool, optional): Se True, caso não exista um órgão
                com o ID especificado, `abort(404)`. O padrão é True.

        Returns:
            Organ: O órgão com o ID especificado.
            None: Caso não exista um órgão com o ID especificado.
        """
        if or_404:
            message = "Órgão não encontrado"
            return Organ.query.filter_by(id=organ_id).first_or_404(message)

        return Organ.query.filter_by(id=organ_id).first()

    def update_organ(
        self,
        organ: Organ,
        form: Dict[str, Any],
    ) -> Organ:
        """Atualiza um órgão com base em seus dados

        Args:
            organ (Organ): O órgão a ser atualizado
            form (Dict[str, Any]): Os dados a serem atualizados

        Returns:
            Organ: O órgão atualizado
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
            organ_id (int): O ID do órgão a ser pesquisado.

        Return:
            list[Institution]: Uma lista de objetos Institution associados
                ao usuário e órgão especificado.
        """
        ...

    def get_institutions(
        self,
        user_id: int,
        *,
        organ_id: Optional[int] = None,
    ) -> List[Institution]:
        """Obtém instituições associadas a um usuário com base em seu ID e o órgão

        Args:
            user_id (int): O ID do usuário
            organ_id (Optional[int], optional): O ID do órgão. Defaults to None.

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
        Relacionado à esta análise cria Análise de Risco e Análise de Vulnerabilidade

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

        for vuln_category in VulnerabilityCategory.query.filter_by(
            is_template=True
        ).all():
            new_vuln_category = VulnerabilityCategory(
                name=vuln_category.name,
                is_template=False,
                analysis_vulnerability_id=new_analysis_vulnerability.id,
            )
            self.__db.session.add(new_vuln_category)
            self.__db.session.commit()

            for vuln_subcategory in VulnerabilitySubCategory.query.filter_by(
                category_id=vuln_category.id, is_template=True
            ).all():
                new_vuln_subcategory = VulnerabilitySubCategory(
                    name=vuln_subcategory.name,
                    category_id=new_vuln_category.id,
                    is_template=False,
                )
                self.__db.session.add(new_vuln_subcategory)
                self.__db.session.commit()

                for vuln in Vulnerability.query.filter_by(
                    sub_category_id=vuln_subcategory.id, is_template=True
                ).all():
                    new_vuln = Vulnerability(
                        name=vuln.name,
                        description=vuln.description,
                        sub_category_id=new_vuln_subcategory.id,
                        is_template=False,
                    )
                    self.__db.session.add(new_vuln)
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

    def get_vuln_factor(
        self, analysis_vulnerability: AnalysisVulnerability
    ) -> float:
        """Retorna o fator de vulnerabilidade de uma dada analise de vulnerabilidade"""

        experts = getattr(
            self.get_analysis(analysis_vulnerability.analysis_id),
            "experts",
            [],
        )
        experts_count = len(experts)

        categories = getattr(
            analysis_vulnerability, "vulnerability_categories", []
        )

        m_categories = []  # média das categorias
        for category in categories:
            subcategories = VulnerabilitySubCategory.query.filter_by(
                category_id=category.id, is_template=False
            ).all()

            m_subs = []  # média das subcategorias

            for subcategory in subcategories:
                vulnerabilities = Vulnerability.query.filter_by(
                    sub_category_id=subcategory.id, is_template=False
                ).all()

                m_vulns = []  # médias das vulnerabilidades
                for vuln in vulnerabilities:
                    vuln_scores = VulnerabilityScore.query.filter_by(
                        vulnerability_id=vuln.id
                    ).all()

                    # média da vulnerabilidade
                    m_vuln = (
                        sum(score.score for score in vuln_scores)
                        / experts_count
                        if experts_count > 0
                        else 0
                    )
                    m_vulns.append(m_vuln)

                # média da subcategoria
                m_sub = sum(m_vulns) / len(m_vulns) if len(m_vulns) > 0 else 0
                m_subs.append(m_sub)

            # média da categoria
            m_category = sum(m_subs) / len(m_subs) if len(m_subs) > 0 else 0
            m_categories.append(m_category)

        # fator de vulnerabilidade
        return (
            sum(m_categories) / len(m_categories)
            if len(m_categories) > 0
            else 0
        )

    def get_threat_score(self, threat: Threat, analysis: Analysis) -> float:
        """Retorna o score de uma dada ameaça

        Args:
            threat (Threat): ameaça

        Returns:
            float: score
        """

        experts = getattr(analysis, "experts", [])
        adverse_actions = AdverseAction.query.filter_by(
            threat_id=threat.id
        ).all()

        m_adverse_actions = []
        for adverse_action in adverse_actions:
            scores = AdverseActionScore.query.filter_by(
                adverse_action_id=adverse_action.id
            ).all()
            m_adverse_action = (
                sum(
                    (score.capacity + score.motivation + score.accessibility)
                    / 3
                    for score in scores
                )
                / len(scores)
                if len(scores) > 0
                else 0
            )
            m_adverse_actions.append(m_adverse_action)

        return sum(m_adverse_actions) / len(experts) if len(experts) > 0 else 0

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

        analysis_vulnerability = analysis.analysis_vulnerability

        if not analysis_vulnerability:
            return []

        actives = Active.query.filter_by(
            analysis_risk_id=analysis_risk.id
        ).all()

        if with_average_scores:
            _actives = []
            for active in actives:
                active_scores: List[ActiveScore] = ActiveScore.query.filter_by(
                    active_id=active.id
                ).all()

                denominator = (
                    len(active_scores) if len(active_scores) > 0 else 1
                )

                _active = active.to_dict()
                _active["average_substitutability"] = sum(
                    score.substitutability for score in active_scores
                ) / (denominator)

                _active["average_replacement_cost"] = sum(
                    score.replacement_cost for score in active_scores
                ) / (denominator)

                _active["average_essentiality"] = sum(
                    score.essentiality for score in active_scores
                ) / (denominator)

                _active["score"] = (
                    _active["average_substitutability"]
                    + _active["average_replacement_cost"]
                    + _active["average_essentiality"]
                ) / 3

                _active["threats"] = []
                for threat in active.associated_threats:
                    threat_score = self.get_threat_score(threat, analysis)
                    threat_adverse_actions = self.get_adverse_actions(
                        threat_id=threat.id
                    )
                    threat = threat.to_dict()
                    threat["score"] = threat_score
                    threat["adverse_actions"] = threat_adverse_actions
                    _active["threats"].append(threat)

                _actives.append(_active)
            actives = _actives

        return actives

    def get_expert_stats(
        self, expert_id: int, analysis: Analysis
    ) -> Tuple[int, int]:
        expert = [e for e in getattr(analysis, "experts") if e.id == expert_id]
        if not expert:
            raise KeyError("Especialista não encontrado")

        expert = expert[0]
        scored = 0
        total = 0
        analysis_risk = AnalysisRisk.query.filter_by(
            analysis_id=analysis.id
        ).first()
        if not analysis_risk:
            raise KeyError("Analise de risco não encontrada")

        # Obtém scores de ativos
        actives = getattr(analysis_risk, "associated_actives")
        total += len(actives)

        for active in actives:
            active_score = ActiveScore.query.filter_by(
                active_id=active.id,
                user_id=expert.id,
            ).first()

            if active_score:
                scored += 1

            # Obtém scores de ações adversas
            threats = getattr(active, "associated_threats")
            for threat in threats:
                adverse_actions = AdverseAction.query.filter_by(
                    threat_id=threat.id
                ).all()
                total += len(adverse_actions)
                for adverse_action in adverse_actions:
                    adverse_action_score = AdverseActionScore.query.filter_by(
                        adverse_action_id=adverse_action.id, user_id=expert.id
                    ).first()
                    if adverse_action_score:
                        scored += 1

        # Obtém scores de Vulnerabilidades
        analysis_vulnerability = getattr(analysis, "analysis_vulnerability")
        if not analysis_vulnerability:
            raise KeyError("Analise de Vulnerabilidade não encontrada")

        vulnerability_categories = getattr(
            analysis_vulnerability, "vulnerability_categories"
        )
        for vuln_category in vulnerability_categories:
            vuln_subcategories = VulnerabilitySubCategory.query.filter_by(
                category_id=vuln_category.id
            ).all()
            for vuln_subcategory in vuln_subcategories:
                vulns = Vulnerability.query.filter_by(
                    sub_category_id=vuln_subcategory.id,
                ).all()
                total += len(vulns)
                for vuln in vulns:
                    vuln_score = VulnerabilityScore.query.filter_by(
                        vulnerability_id=vuln.id, user_id=expert.id
                    ).first()
                    if vuln_score:
                        scored += 1

        return scored, total

    def update_adverse_actions_score(
        self,
        adverse_action_id: int,
        scores: Dict[str, Any],
        user_id: int,
    ) -> None:
        """
        Atualiza a pontuação de uma ação adversa.

        Args:
            adverse_action_id (int): O ID da ação adversa.
            scores (Dict[str, Any]): Um dicionário contendo as
                pontuações a serem atualizadas para a ação adversa.
            user_id (User | Any): O ID do usuário cuja pontuação
                está sendo atualizada.

        Returns:
            AdverseActionScore | None: O objeto AdverseActionScore
                atualizado se a atualização for bem-sucedida, None
                caso contrário.
        """
        adverse_action_score = AdverseActionScore.query.filter_by(
            adverse_action_id=adverse_action_id,
            user_id=user_id,
        ).first()

        if adverse_action_score:
            for score, value in scores.items():
                setattr(adverse_action_score, score, value)
        else:
            adverse_action_score = AdverseActionScore(
                **scores,
                adverse_action_id=adverse_action_id,
                user_id=user_id,
            )
            self.__db.session.add(adverse_action_score)

        self.__db.session.commit()

    def update_active_score(
        self, active_id: int, scores: Dict[str, Any], user_id: int
    ) -> None:
        """
        Atualiza a pontuação de um ativo.
        """

        active_score = ActiveScore.query.filter_by(
            active_id=active_id,
            user_id=user_id,
        ).first()

        for score, value in scores.items():
            setattr(active_score, score, value)

        self.__db.session.commit()

    def update_vulnerability_score(
        self, vuln_id: int, score: float, user_id: int
    ) -> None:
        """
        Atualiza a pontuação de uma vulnerabilidade.
        """
        print("vuln_id", vuln_id)
        print("user_id", user_id)
        print("score", score)
        vuln_score = VulnerabilityScore.query.filter_by(
            vulnerability_id=vuln_id, user_id=user_id  # type: ignore
        ).first()

        print(vuln_score)

        setattr(vuln_score, "score", score)

        self.__db.session.commit()

    def get_experts_by_analysis(
        self,
        analysis: Analysis,
    ):
        experts = getattr(analysis, "experts", [])
        for expert in experts:
            scored, total = database_manager.get_expert_stats(
                expert.id, analysis
            )
            expert.scored = scored
            expert.not_scored = total - scored
            expert.total = total
            expert.average_score = scored / total if total > 0 else 0

        return experts

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

    def add_active_score(self, **kwargs) -> ActiveScore:
        """Adiciona uma pontuação de um ativo ao banco de dados"""
        active_score = ActiveScore(**kwargs)

        self.__db.session.add(active_score)
        self.__db.session.commit()

        return active_score

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

    def get_experts_by_threat(self, threat_id: int) -> List[User]:
        """Obtém os experts relacionados à uma Análise -> Análise de Risco -> Ativo -> Ameaça"""

        _threat = self.get_threat(threat_id)
        _active = self.get_active(getattr(_threat, "active_id"))
        _analysis_risk = self.get_analysis_risk(
            getattr(_active, "analysis_risk_id")
        )
        _analysis = self.get_analysis(getattr(_analysis_risk, "analysis_id"))
        return self.get_experts_by_analysis(_analysis)  # type: ignore

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
                (Caso `with_scores=True`). Padrão é None.
                Caso user_id = None, então todos os usuários serão considerados.

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
                    adverse_action_id=adverse_action["id"]
                )
                if user_id:
                    adverse_action_scores = adverse_action_scores.filter_by(
                        user_id=user_id
                    ).first()
                else:
                    experts = self.get_experts_by_threat(threat_id)
                    experts_count = len(experts)

                    adverse_action_scores = adverse_action_scores.all()

                    motivation, capacity, accessibility = (0, 0, 0)
                    for adverse_action_score in adverse_action_scores:
                        motivation += adverse_action_score.motivation
                        capacity += adverse_action_score.capacity
                        accessibility += adverse_action_score.accessibility

                    motivation /= experts_count if experts_count > 0 else 1
                    capacity /= experts_count if experts_count > 0 else 1
                    accessibility /= experts_count if experts_count > 0 else 1

                    adverse_action_scores = AdverseActionScore(
                        motivation=int(motivation),
                        capacity=int(capacity),
                        accessibility=int(accessibility),
                        user_id=0,
                        adverse_action_id=0,
                    )

                adverse_action["scores"] = (
                    adverse_action_scores.as_dict()
                    if adverse_action_scores
                    else {}
                )
                adverse_action["score"] = (
                    adverse_action["scores"].get("motivation", 0)
                    + adverse_action["scores"].get("capacity", 0)
                    + adverse_action["scores"].get("accessibility", 0)
                ) / 3

            _new_adverse_actions.append(adverse_action)

        return _new_adverse_actions

    def add_vulnerability_category(self, name: str) -> None:
        """Adiciona uma nova categoria de vulnerabilidade

        Args:
            name (str): Nome da nova categoria de vulnerabilidade
        """

        vulnerability_category = VulnerabilityCategory(
            name=name, is_template=True
        )

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
            name=name, is_template=True
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
    ) -> None:
        """Adiciona uma nova vulnerabilidade

        Args:
            name (str): Nome da nova vulnerabilidade
            description (str): Descrição da nova vulnerabilidade
            sub_category_id (int): ID da subcategoria à qual a vulnerabilidade pertence
        """

        vulnerability = Vulnerability(
            name=name, description=description, is_template=True
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

    def get_vulns_category_by_analysis_vulnerability_id(
        self,
        av_id: int,
    ) -> List[VulnerabilityCategory]:
        return VulnerabilityCategory.query.filter_by(
            analysis_vulnerability_id=av_id, is_template=False
        ).all()

    def get_vuln_sub_categories_by_category_id(
        self, category_id: int
    ) -> List[VulnerabilitySubCategory]:
        return VulnerabilitySubCategory.query.filter_by(
            category_id=category_id, is_template=False
        ).all()

    def get_vulnerabilities_by_subcategory_id(
        self, sc_id: int
    ) -> List[Vulnerability]:
        return Vulnerability.query.filter_by(
            sub_category_id=sc_id, is_template=False
        ).all()

    def get_vuln_score_by_user(
        self, vulnerability_id: int, user_id: int
    ) -> int:
        score = VulnerabilityScore.query.filter_by(
            vulnerability_id=vulnerability_id, user_id=user_id
        ).first()

        if not score:
            score = VulnerabilityScore(
                vulnerability_id=vulnerability_id, user_id=user_id
            )
            self.__db.session.add(score)
            self.__db.session.commit()

        return score.score

    def delete_category(self, category_id: int) -> None:
        VulnerabilityCategory.query.filter_by(id=category_id).delete()
        self.__db.session.commit()


database_manager = DatabaseManager()
