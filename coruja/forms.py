from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    FieldList,
    HiddenField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    Regexp,
    ValidationError,
)

from .utils import UniqueData


def validate_cpf(form, field):
    """
    Valida o número de CPF inserido no formulário.
    Parameters:
        - form (FlaskForm): O formulário FlaskForm atual.
        - field (StringField): O campo de CPF no formulário.
    Raise:
        - ValidationError: Se o CPF não for válido (não numérico ou não
            tem 11 dígitos).
    """
    cpf = field.data
    if not cpf.isnumeric() or len(cpf) != 11:
        raise ValidationError("CPF Inválido")


class LoginForm(FlaskForm):
    """
    Formulário de login.
    Fields:
        - cpf (StringField): O campo para inserir o CPF do usuário.
        - password (PasswordField): O campo para inserir a senha do usuário.
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
    """

    cpf = StringField(
        label="CPF",
        validators=[DataRequired("Preencha esse campo"), validate_cpf],
        description="Somente Números",
    )
    password = PasswordField(
        label="Senha", validators=[DataRequired("Preencha esse campo")]
    )
    submit = SubmitField(label="Entrar")
    csrf_token = HiddenField()


class OrganForm(FlaskForm):
    """
    Formulário para criar um órgão.

    Fields:
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
        - name (str): O campo para inserir o nome do órgão.
        - cnpj (str): O campo para inserir o CNPJ do órgão.
        - address (str): O campo para inserir o endereço do órgão.
        - email (str): O campo para inserir o e-mail do órgão.
        - telephone (str): O campo para inserir o telefone do órgão.
    """

    csrf_token = HiddenField()
    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    cnpj = StringField(
        "CNPJ",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^\d{2}.\d{3}.\d{3}\/\d{4}-\d{2}$",
                message="Insira um CNPJ válido",
            ),
            UniqueData(
                message="Este CNPJ já está associado a outro orgão ou instituição",
            ),
        ],
    )
    address = StringField(
        "Endereço",
        validators=[DataRequired("Este campo é obrigatório")],
    )
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Email("Digite um endereço de e-mail válido"),
            UniqueData(
                message="Este e-mail já está associado a outro orgão ou instituição",
            ),
        ],
    )
    telephone = StringField(
        "Telefone",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^(\(\d{2,3}\) \d{4,5}-\d{4}|\d{10,11})$",
                message="Formato de telefone inválido",
            ),
            UniqueData(
                message="Este telefone já está associado a outro orgão ou instituição",
            ),
        ],
    )
    admin_ids = FieldList(HiddenField(), min_entries=1)
    submit = SubmitField("Criar orgão")

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop("is_edit", False)
        self.obj = kwargs.get("obj", None)

        super().__init__(*args, **kwargs)


class InstitutionForm(FlaskForm):
    """
    Formulário para criar uma instituição.

    Fields:
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
        - name (str): O campo para inserir o nome da instituição.
        - address (str): O campo para inserir o endereço da instituição.
        - description (str): O campo para inserir a descrição da instituição.
        - cnpj (str, optional): O campo para inserir o CNPJ da instituição.
    """

    csrf_token = HiddenField()
    name = StringField(
        "Nome",
        validators=[DataRequired("Este campo é obrigatório")],
    )
    cnpj = StringField(
        "CNPJ",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^\d{2}.\d{3}.\d{3}\/\d{4}-\d{2}$",
                message="Insira um CNPJ válido",
            ),
            UniqueData(
                message="Este CNPJ já está associado a outro orgão ou instituição",
            ),
        ],
    )
    address = StringField(
        "Endereço",
        validators=[DataRequired("Este campo é obrigatório")],
    )
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Email("Digite um endereço de e-mail válido"),
            UniqueData(
                message="Este e-mail já está associado a outro orgão ou instituição",
            ),
        ],
    )
    telephone = StringField(
        "Telefone",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^(\(\d{2,3}\) \d{4,5}-\d{4}|\d{10,11})$",
                message="Formato de telefone inválido. Use (99) 99999-9999.",
            ),
            UniqueData(
                message="Este telefone já está associado a outro orgão ou instituição",
            ),
        ],
    )
    admin_ids = FieldList(HiddenField(), min_entries=1)
    submit = SubmitField("Criar instituição")

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop("is_edit", False)
        self.obj = kwargs.get("obj", None)
        super().__init__(*args, **kwargs)


class UnitForm(FlaskForm):
    """
    Formulário para criar uma Unidade.

    Fields:
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
        - name (str): O campo para inserir o nome da unidade.
        - address (str): O campo para inserir o endereço da unidade.
        - description (str, optional): O campo para inserir a descrição da unidade.
    """

    csrf_token = HiddenField()
    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    address = StringField(
        "Endereço", validators=[DataRequired("Este campo é obrigatório")]
    )
    description = StringField("Descrição")
    admin_ids = FieldList(HiddenField(), min_entries=1)
    submit = SubmitField("Criar instituição")


class AnalysisForm(FlaskForm):
    """
    Formulário para criar / editar uma análise.
    Fields:
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
        - description (str): O campo para inserir a descrição da análise.
    """

    csrf_token = HiddenField()
    description = StringField("Descrição")
    admin_ids = FieldList(HiddenField(), min_entries=1)
    expert_ids = FieldList(HiddenField(), min_entries=1)
    submit = SubmitField("Submeter")


class VulnerabilityCategoryForm(FlaskForm):
    """
    Formulário para criar uma categoria de vulnerabilidade.

    Fields:
        - name (str): O campo para inserir o nome da categoria.
        - analysis_vulnerability_id (HiddenField): O campo para selecionar o ID de análise de vulnerabilidade.
        - is_template (HiddenField): O campo para indicar se a categoria é um template.
        - submit (SubmitField): O botão de envio do formulário.
    """

    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    analysis_vulnerability_id = HiddenField(validators=[Optional()])
    is_template = HiddenField(validators=[Optional()])
    submit = SubmitField("Criar Categoria de Vulnerabilidade")


class VulnerabilitySubcategoryForm(FlaskForm):
    """
    Formulário para criar uma categoria de vulnerabilidade.

    Fields:
        - name (str): O campo para inserir o nome da categoria.
        - analysis_vulnerability_id (HiddenField): O campo para selecionar o ID de análise de vulnerabilidade.
        - is_template (HiddenField): O campo para indicar se a categoria é um template.
        - submit (SubmitField): O botão de envio do formulário.
    """

    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    analysis_vulnerability_id = HiddenField(validators=[Optional()])
    is_template = HiddenField(validators=[Optional()])
    submit = SubmitField("Criar Subcategoria de Vulnerabilidade")


class UserForm(FlaskForm):
    csrf_token = HiddenField()
    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    title = StringField("Título")
    cpf = StringField(
        "CPF",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^\d{3}.\d{3}.\d{3}-\d{2}$",
                message="Insira um CPF válido",
            ),
            UniqueData(
                message="Este CPF já está associado a outro usuário",
            ),
        ],
    )
    email_personal = EmailField(
        "E-mail pessoal",
        validators=[
            Optional(),
            Email("Digite um endereço de e-mail válido"),
            UniqueData(
                message="Este e-mail já está associado a outro usuário",
            ),
        ],
    )
    email_professional = EmailField(
        "E-mail profissional",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Email("Digite um endereço de e-mail válido"),
            UniqueData(
                message="Este e-mail já está associado a outro usuário"
            ),
        ],
    )
    password = PasswordField(
        "Senha",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Length(
                min=8, message="A senha precisa ter no mínimo 8 caracteres"
            ),
        ],
    )
    _telephones = FieldList(
        StringField(
            "Telefones",
            validators=[
                Regexp(
                    r"^(\(\d{2,3}\) \d{4,5}-\d{4}|\d{10,11})$",
                    message="Formato de telefone inválido",
                ),
                UniqueData(
                    message="Este telefone já está associado a outro usuário, orgão ou instituição",
                ),
            ],
        )
    )
    address = StringField("Endereço")
    submit = SubmitField("Criar usuário")

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop("is_edit", False)
        self.obj = kwargs.get("obj", None)
        super().__init__(*args, **kwargs)


class VulnerabilityForm(FlaskForm):
    """
    Formulário para criar uma vulnerabilidade.

    Fields:
        - name (str): O campo para inserir o nome da vulnerabilidade.
        - description (TextAreaField): O campo para inserir a descrição da vulnerabilidade.
        - sub_category_id (HiddenField): O campo para selecionar o ID da subcategoria.
        - is_template (HiddenField): O campo para indicar se a vulnerabilidade é um template.
        - submit (SubmitField): O botão de envio do formulário.
    """

    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    description = StringField("Descrição")
    sub_category_id = HiddenField(validators=[Optional()])
    is_template = HiddenField(validators=[Optional()])
    submit = SubmitField("Criar Vulnerabilidade")


class DefaultForm(FlaskForm):
    """
    Formulário padrão para Ativos, Ameaças e Ações Adversas

    Fiels:
        - title (str): O campo para inserir o titulo.
        - description (str): O campo para inserir a descrição.
        - is_template (HiddenField): O campo para indicar se é um template.
    """

    title = StringField("Título", validators=[DataRequired()])
    description = StringField("Descrição", validators=[Optional()])
    # is_template = HiddenField(validators=[Optional()])
    submit = SubmitField("Criar")
