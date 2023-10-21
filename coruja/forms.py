from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    FieldList,
    HiddenField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Regexp, ValidationError


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

    # total_sum = 0
    # weight = 10

    # # Calcula o primeiro dígito verificador
    # for n in cpf[:-2]:
    #     total_sum += int(n) * weight
    #     weight -= 1

    # verifying_digit = 11 - (total_sum % 11)
    # verifying_digit = 0 if verifying_digit > 9 else verifying_digit

    # if verifying_digit != int(cpf[-2]):
    #     raise ValidationError("CPF Inválido")

    # # Calcula o segundo dígito verificador
    # total_sum = 0
    # weight = 11
    # for n in cpf[:-1]:
    #     total_sum += int(n) * weight
    #     weight -= 1

    # verifying_digit = 11 - (total_sum % 11)
    # verifying_digit = 0 if verifying_digit > 9 else verifying_digit

    # if verifying_digit != int(cpf[-1]):
    #     raise ValidationError("CPF Inválido")


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
        ],
    )
    address = StringField("Endereço")
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Email("Digite um endereço de e-mail válido"),
        ],
    )
    telephone = StringField(
        "Telefone",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^\(\d{2,3}\) \d{4,5}-\d{4}$",
                message="Formato de telefone inválido. Use (99) 99999-9999.",
            ),
        ],
    )
    admin_ids = FieldList(HiddenField(), min_entries=1)
    submit = SubmitField("Criar orgão")


class InstitutionForm(FlaskForm):
    """
    Formulário para criar uma instituição.

    Fields:
        - csrf_token (HiddenField): O campo oculto para proteção CSRF.
        - name (str): O campo para inserir o nome da instituição.
        - address (str): O campo para inserir o endereço da instituição.
        - description (str): O campo para inserir a descrição da instituição.
    """

    csrf_token = HiddenField()
    name = StringField(
        "Nome", validators=[DataRequired("Este campo é obrigatório")]
    )
    address = StringField("Endereço")
    description = StringField("Descrição")
    cnpj = StringField(
        "CNPJ",
        validators=[
            Regexp(
                r"^\d{2}.\d{3}.\d{3}\/\d{4}-\d{2}$",
                message="Insira um CNPJ válido",
            ),
        ],
    )
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Email("Digite um endereço de e-mail válido"),
        ],
    )
    telephone = StringField(
        "Telefone",
        validators=[
            DataRequired("Este campo é obrigatório"),
            Regexp(
                r"^\(\d{2,3}\) \d{4,5}-\d{4}$",
                message="Formato de telefone inválido. Use (99) 99999-9999.",
            ),
        ],
    )
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
    expert_ids = FieldList(HiddenField())
    submit = SubmitField("Submeter")
