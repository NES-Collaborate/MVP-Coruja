## MVP do Projeto Coruja

Mínimo Produto Viável (MVP) de uma aplicação Web para gerenciamento de cargos e permissões em uma organização composta por órgãos, instituições, análises de risco e ativos. Além de possibilitar a realização de avaliações de ameaças e ações adversas, assim como a atribuição de notas por especialistas independentemente.

## **Deploy**

Este projeto contém Flask como aplicação web configurado com o servidor uWSGI, NGinx como proxy reverso, e Alembic para migrações no banco MySQL, sendo tudo gerenciado pelo Docker Compose. Siga as seguintes instruções para executar o projeto:

1. Clone este repositório;
2. Modifique o arquivo `.env` adicionando uma senha e nome do banco de dados de sua escolha;
3. Modifique o arquivo `.secrets.toml` adicionando uma chave secreta para a aplicação;
4. Executa `docker-compose up -d`.
5. Acesse http://localhost . O nome do servidor está configurado no `server_name` no `nginx.conf`.

## :rotating_light: **Licença**

Este MVP está distribuído sobre a licença Apache 2.0. Para saber mais, acesse [LICENSE](/LICENSE).
