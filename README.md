# DataLake

## Sobre o projeto

O DataLake é uma plataforma educacional de engenharia de dados em saúde. O projeto simula, em menor escala, os desafios encontrados na integração de informações produzidas por laboratórios, clínicas, hospitais, instituições de pesquisa e outros sistemas de saúde.

No MVP 0.2.0, o foco está na modelagem inicial do domínio e no versionamento da estrutura do banco. O projeto utiliza modelos SQLAlchemy e migrações Alembic para criar e evoluir o PostgreSQL de forma reproduzível.

> O projeto utiliza somente dados sintéticos, fictícios, públicos ou adequadamente anonimizados. Dados clínicos reais e informações pessoais não devem ser adicionados ao repositório.

## Problema

Sistemas de saúde podem representar informações equivalentes com nomes, estruturas, formatos, códigos e unidades diferentes. Essas diferenças dificultam a consolidação, a validação e a análise conjunta dos dados, além de prejudicarem a identificação de sua origem e das transformações aplicadas durante o processamento.

Sem um fluxo padronizado e rastreável, podem surgir registros duplicados, valores inválidos, informações incompletas, falhas silenciosas e perda da relação entre o dado armazenado e sua fonte.

## Objetivo

O objetivo do projeto é desenvolver progressivamente uma plataforma capaz de receber, validar, transformar, armazenar e disponibilizar dados de saúde de maneira segura, organizada e rastreável.

No MVP 0.2.0, o objetivo específico é representar o domínio inicial de dados laboratoriais, separar os dados entre os schemas `ingestion` e `core` e criar toda a estrutura do banco por migrações reversíveis.

A visão completa do produto está documentada em [`docs/project-vision.md`](docs/project-vision.md).

## Arquitetura atual

```text
Projeto DataLake
       │
       ├── Configurações
       ├── Modelos SQLAlchemy
       └── Migrações Alembic
                │
                ▼
           PostgreSQL
                │
       ┌────────┴────────┐
       ▼                 ▼
   ingestion            core
       │                 │
 data_sources       patients
                    exam_types
                    biological_samples
                    laboratory_exams
                    exam_results
```

As configurações são carregadas do arquivo `.env`. O SQLAlchemy representa as tabelas e suas regras de integridade, enquanto o Alembic cria e versiona a estrutura do banco. O schema `ingestion` registra a origem dos dados e o schema `core` concentra os dados tratados do domínio.

O Docker Compose declara o serviço PostgreSQL e torna a infraestrutura reproduzível. O health check utiliza `pg_isready` para confirmar que o banco está aceitando conexões, enquanto o volume nomeado preserva os dados quando o contêiner é recriado.

## Tecnologias

- Python 3.12 ou superior;
- PostgreSQL 17;
- Docker Desktop;
- Docker Compose;
- SQLAlchemy 2;
- Psycopg 3;
- Pydantic Settings;
- Alembic;
- Pytest;
- Git.

## Pré-requisitos

Antes de executar o projeto, instale:

- [Git](https://git-scm.com/);
- [Python](https://www.python.org/downloads/) 3.12 ou superior;
- [Docker Desktop](https://www.docker.com/products/docker-desktop/).

Verifique as instalações no PowerShell:

```powershell
git --version
docker --version
docker compose version
py --version
```

O Docker Desktop deve estar aberto e com o mecanismo em execução.

## Como executar

### 1. Clonar o repositório

```powershell
git clone https://github.com/marianagpalacios/DataLake.git
cd DataLake
```

### 2. Criar o arquivo `.env`

Copie o modelo público de configuração:

```powershell
Copy-Item .env.example .env
```

Abra o `.env` e substitua o valor de `POSTGRES_PASSWORD` por uma senha local segura. Não envie esse arquivo ao Git.

### 3. Criar o ambiente virtual

```powershell
python -m venv .venv
```

Ative o ambiente no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se a política de execução bloquear a ativação, libere scripts somente para a sessão atual e tente novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar o projeto

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Valide a instalação:

```powershell
python -c "import datalake; print('Pacote DataLake importado com sucesso.')"
```

### 5. Iniciar o PostgreSQL

Valide a configuração antes de iniciar o serviço:

```powershell
docker compose config --quiet
```

Em seguida, inicie o PostgreSQL em segundo plano:

```powershell
docker compose up -d
```

### 6. Aplicar as migrações

Crie os schemas e as tabelas na versão mais recente:

```powershell
python -m alembic upgrade head
```

### 7. Verificar o serviço

```powershell
docker compose ps
```

Após alguns segundos, o serviço deverá aparecer como `healthy`. Se aparecer `health: starting`, aguarde e execute o comando novamente.

Para consultar os logs:

```powershell
docker compose logs postgres
```

### 8. Executar os testes

```powershell
python -m pytest
```

### 9. Conectar-se ao banco

```powershell
docker compose exec postgres psql -U datalake_user -d datalake
```

No terminal do PostgreSQL, execute:

```sql
SELECT current_database();
SELECT current_user;
SELECT version();
```

Para sair do `psql`:

```text
\q
```

## Comandos úteis

Iniciar os serviços:

```powershell
docker compose up -d
```

Verificar o estado:

```powershell
docker compose ps
```

Consultar os logs:

```powershell
docker compose logs postgres
```

Acompanhar os logs em tempo real:

```powershell
docker compose logs -f postgres
```

Parar e remover os contêineres e a rede, preservando o volume:

```powershell
docker compose down
```

Validar a conexão por meio de um único comando:

```powershell
docker compose exec postgres psql -U datalake_user -d datalake -c "SELECT current_database(), current_user;"
```

### Migrações do banco

Aplicar todas as migrações:

```powershell
python -m alembic upgrade head
```

Verificar a migração atual:

```powershell
python -m alembic current
```

Consultar o histórico:

```powershell
python -m alembic history
```

Reverter a migração mais recente:

```powershell
python -m alembic downgrade -1
```

> Não execute `docker compose down -v` sem compreender o impacto. A opção `-v` remove o volume e apaga os dados armazenados no PostgreSQL.

## Estrutura de diretórios

```text
DataLake/
├── alembic/
│   ├── versions/
│   │   └── *_create_initial_database_schema.py
│   ├── README
│   ├── env.py
│   └── script.py.mako
├── data/
│   ├── processed/
│   │   └── .gitkeep
│   ├── raw/
│   │   └── .gitkeep
│   └── rejected/
│       └── .gitkeep
├── docs/
│   ├── database-model.md
│   └── project-vision.md
├── src/
│   └── datalake/
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── database/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── engine.py
│       │   ├── health.py
│       │   └── session.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── biological_sample.py
│       │   ├── data_source.py
│       │   ├── exam_result.py
│       │   ├── exam_type.py
│       │   ├── laboratory_exam.py
│       │   └── patient.py
│       └── __init__.py
├── tests/
│   ├── integration/
│   │   └── test_database_connection.py
│   └── unit/
│       ├── test_models.py
│       └── test_settings.py
├── .editorconfig
├── .env.example
├── .gitignore
├── alembic.ini
├── compose.yaml
├── pyproject.toml
└── README.md
```

- `data/raw`: dados recebidos sem transformação;
- `data/processed`: dados processados e aceitos;
- `data/rejected`: dados rejeitados durante validações futuras;
- `docs`: documentação do produto e da arquitetura;
- `src/datalake/config`: carregamento e validação das configurações;
- `src/datalake/database`: base declarativa, conexão e sessões do banco;
- `src/datalake/models`: modelos SQLAlchemy do domínio;
- `alembic`: configuração e versões das migrações;
- `tests`: testes unitários e de integração.

Os diretórios de dados mantêm somente arquivos `.gitkeep` no Git. Seu conteúdo local é ignorado para reduzir o risco de exposição acidental de dados sensíveis.

## Roadmap

- [x] MVP 0.1.0 — estrutura inicial do projeto Python;
- [x] MVP 0.1.0 — PostgreSQL com Docker Compose;
- [x] MVP 0.1.0 — volume persistente e health check;
- [x] MVP 0.1.0 — configuração por variáveis de ambiente;
- [ ] MVP 0.2.0 — modelagem inicial do domínio;
- [ ] MVP 0.2.0 — SQLAlchemy e migrações com Alembic;
- [ ] Ingestão e validação de arquivos;
- [ ] Pipeline ETL;
- [ ] API REST;
- [ ] Testes automatizados e integração contínua;
- [ ] Indicadores e visualizações.

## Segurança e dados

- O arquivo `.env` contém configurações locais e nunca deve ser versionado.
- O `.env.example` serve apenas como modelo e não deve conter senhas reais.
- Senhas, tokens e outras credenciais não devem ser incluídos no código, em commits, issues ou documentação.
- Dados de pacientes e informações pessoais não devem ser enviados ao repositório.
- A saída completa de `docker compose config` pode revelar os valores do `.env`; não a publique.
- Antes de cada commit, utilize `git status` e revise o conteúdo preparado com `git diff --cached`.

## Status do projeto

**MVP 0.2.0 — Modelagem inicial e migrações concluídas.**

O banco possui schemas separados para ingestão e dados tratados,
modelos SQLAlchemy, constraints de integridade e migrações Alembic
reversíveis.