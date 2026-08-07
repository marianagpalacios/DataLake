# Estratégia de testes do DataLake

## 1. Objetivo

Garantir que os testes do DataLake sejam isolados, reproduzíveis e
incapazes de alterar o banco de desenvolvimento.

## 2. Categorias

### Testes unitários

Testam funções ou classes isoladamente, sem PostgreSQL.

### Testes de integração

Testam a comunicação entre Python, SQLAlchemy, Psycopg e PostgreSQL.

### Testes da API

Testam contratos HTTP, filtros, paginação, erros e respostas.

### Testes das migrações

Criam um banco temporário e verificam upgrade e downgrade.

## 3. Banco exclusivo

Os testes utilizam:

- banco: `datalake_test`;
- porta local: `5433`;
- arquivo: `.env.test`;
- Compose: `compose.test.yaml`.

## 4. Segurança

A suíte deve interromper imediatamente se o banco configurado não
possuir um nome explicitamente destinado a testes.

## 5. Migrações

As migrations do Alembic são aplicadas automaticamente no início da
sessão de testes.

## 6. Isolamento

As tabelas são limpas antes e depois de cada teste de integração.

## 7. Fixtures

Fixtures centralizam:

- configurações;
- engine;
- session factory;
- migrations;
- cliente FastAPI;
- limpeza do banco;
- criação de dados sintéticos.

## 8. Cobertura

A cobertura considera linhas e branches.

A meta mínima final do MVP é 80%.

## 9. Comandos

### Unitários

`python -m pytest -m unit`

### Integração

`python -m pytest -m integration`

### API

`python -m pytest -m api`

### Migrações

`python -m pytest -m migration`

### Cobertura

`python -m pytest --cov=datalake --cov-branch --cov-report=term-missing`