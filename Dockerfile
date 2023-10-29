FROM python

# Configuração das variáveis de ambiente
ENV PYTHON_VERSION 3.11.0
ENV FLASK_APP coruja.app:create_app
ENV FLASK_ENV production

WORKDIR /MVP-Coruja

COPY requirements.txt .
COPY settings.toml .
COPY .secrets.toml .
COPY Makefile .

RUN pip install --no-cache-dir -r requirements.txt
# Inicialização do banco de dados e migração
RUN python -m flask db init
RUN	python -m flask db migrate
RUN	python -m flask db upgrade
RUN	python -m flask createroles
RUN python -m flask createsu

WORKDIR /MVP-Coruja/coruja

COPY /coruja .

EXPOSE 8000

WORKDIR /MVP-Coruja

CMD ["python", "-m", "flask", "run"]