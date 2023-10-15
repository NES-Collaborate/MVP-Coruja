## MVP do Projeto Coruja

Mínimo Produto Viável (MVP) de uma aplicação Web para gerenciamento de cargos e permissões em uma organização composta por órgãos, instituições, análises de risco e ativos. Além de possibilitar a realização de avaliações de ameaças e ações adversas, assim como a atribuição de notas por especialistas independentemente.

## **Execução**

```bash
# Clone este repositório
$ git clone git@github.com:Coruja-NES/MVP-Coruja.git
# Acesse a pasta do projeto no terminal/cmd
$ cd MVP-Coruja
# Instale as dependências
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -U pip setuptools
$ pip install -r requirements.txt
# Execute a aplicação em modo de desenvolvimento
$ export FLASK_ENV=development
$ export FLASK_APP=coruja.app:create_app
$ make init
# O servidor inciará na porta:5000 - acesse http://localhost:5000
$ make server
```

## :rotating_light: **Licença**

Este MVP está distribuído sobre a licença Apache 2.0. Para saber mais, acesse [LICENSE](/LICENSE).
