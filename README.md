# DataLake

## Sobre o projeto

O DataLake é uma plataforma educacional de engenharia de dados em saúde. O projeto simula, em menor escala, os desafios encontrados na integração de informações produzidas por laboratórios, clínicas, hospitais, instituições de pesquisa e outros sistemas de saúde.

No MVP 0.3.0, o foco está na primeira ingestão de dados externos. O
projeto lê um arquivo CSV de pacientes sintéticos com Pandas, valida e
normaliza seus registros e insere no PostgreSQL somente os pacientes que ainda
não existem.

> O projeto utiliza somente dados sintéticos, fictícios, públicos ou adequadamente anonimizados. Dados clínicos reais e informações pessoais não devem ser adicionados ao repositório.

## Problema

Sistemas de saúde podem representar informações equivalentes com nomes, estruturas, formatos, códigos e unidades diferentes. Essas diferenças dificultam a consolidação, a validação e a análise conjunta dos dados, além de prejudicarem a identificação de sua origem e das transformações aplicadas durante o processamento.

Sem um fluxo padronizado e rastreável, podem surgir registros duplicados, valores inválidos, informações incompletas, falhas silenciosas e perda da relação entre o dado armazenado e sua fonte.

## Objetivo

O objetivo do projeto é desenvolver progressivamente uma plataforma capaz de receber, validar, transformar, armazenar e disponibilizar dados de saúde de maneira segura, organizada e rastreável.

No MVP 0.3.0, o objetivo específico é implementar um fluxo transacional e
idempotente de ingestão de pacientes, mantendo separadas as responsabilidades
de leitura, validação, mapeamento, persistência e apresentação do resultado.

A visão completa do produto está documentada em [`docs/project-vision.md`](docs/project-vision.md).

## Arquitetura atual

```text
Arquivo CSV
    |
    v
Leitor CSV + Pandas
    |
    v
Validação e normalização
    |
    v
Mapper para Patient
    |
    v
Serviço de ingestão
    |
    v
SQLAlchemy
    |
    v
PostgreSQL
    |
    ├── ingestion.data_sources
    └── core
        ├── patients
        ├── exam_types
        ├── biological_samples
        ├── laboratory_exams
        └── exam_results
```

As configurações são carregadas do arquivo `.env`. O leitor transforma o CSV
em um `DataFrame` do Pandas, o validador aplica o contrato de entrada e o mapper
converte os registros normalizados em objetos `Patient`. O serviço consulta os
códigos externos já armazenados, insere somente os pacientes novos e controla
a transação por meio do SQLAlchemy.

O Alembic cria e versiona a estrutura do banco. O schema `ingestion` registra
a origem dos dados e o schema `core` concentra os dados tratados do domínio.

O Docker Compose declara o serviço PostgreSQL e torna a infraestrutura reproduzível. O health check utiliza `pg_isready` para confirmar que o banco está aceitando conexões, enquanto o volume nomeado preserva os dados quando o contêiner é recriado.

## Tecnologias

- Python 3.12 ou superior;
- PostgreSQL 17;
- Docker Desktop;
- Docker Compose;
- Pandas 3;
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

### 8. Executar a ingestão

Importe o arquivo sintético incluído no projeto:

```powershell
python -m datalake.ingestion.cli data/examples/patients.csv
```

O comando valida o arquivo e apresenta as quantidades de registros recebidos,
inseridos e já existentes.

### 9. Executar os testes

```powershell
python -m pytest
```

Para executar somente os testes unitários:

```powershell
python -m pytest -m "not integration"
```

### 10. Conectar-se ao banco

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
│   ├── examples/
│   │   └── patients.csv
│   ├── processed/
│   │   └── .gitkeep
│   ├── raw/
│   │   └── .gitkeep
│   └── rejected/
│       └── .gitkeep
├── docs/
│   ├── database-model.md
│   ├── patient-csv-ingestion.md
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
│       ├── ingestion/
│       │   ├── mappers/
│       │   │   └── patient_mapper.py
│       │   ├── readers/
│       │   │   └── csv_reader.py
│       │   ├── services/
│       │   │   └── patient_ingestion_service.py
│       │   ├── validators/
│       │   │   └── patient_validator.py
│       │   ├── cli.py
│       │   └── exceptions.py
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
│   │   ├── test_database_connection.py
│   │   └── test_patient_ingestion.py
│   └── unit/
│       ├── ingestion/
│       │   ├── test_csv_reader.py
│       │   ├── test_patient_mapper.py
│       │   └── test_patient_validator.py
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

- `data/examples`: arquivos sintéticos seguros para demonstração;
- `data/raw`: dados recebidos sem transformação;
- `data/processed`: dados processados e aceitos;
- `data/rejected`: dados rejeitados durante validações futuras;
- `docs`: documentação do produto e da arquitetura;
- `src/datalake/config`: carregamento e validação das configurações;
- `src/datalake/database`: base declarativa, conexão e sessões do banco;
- `src/datalake/ingestion`: leitura, validação, mapeamento, serviço e CLI;
- `src/datalake/models`: modelos SQLAlchemy do domínio;
- `alembic`: configuração e versões das migrações;
- `tests`: testes unitários e de integração.

Os diretórios `raw`, `processed` e `rejected` mantêm somente arquivos
`.gitkeep` no Git. Seu conteúdo local é ignorado para reduzir o risco de
exposição acidental de dados sensíveis. Apenas arquivos sintéticos preparados
para demonstração podem ser versionados em `data/examples`.

## Roadmap

- [x] MVP 0.1.0 — infraestrutura, Docker e PostgreSQL;
- [x] MVP 0.2.0 — modelagem, SQLAlchemy e Alembic;
- [x] MVP 0.3.0 — primeira ingestão de pacientes por CSV;
- [x] MVP 0.4.0 — validação e qualidade dos dados;
- [ ] MVP 0.5.0 — pipeline ETL, staging e rastreabilidade;
- [ ] MVP 0.6.0 — API REST com FastAPI;
- [ ] MVP 0.7.0 — testes completos e banco de testes;
- [ ] MVP 0.8.0 — GitHub Actions e preparação do portfólio.

## Segurança e dados

- O arquivo `.env` contém configurações locais e nunca deve ser versionado.
- O `.env.example` serve apenas como modelo e não deve conter senhas reais.
- Senhas, tokens e outras credenciais não devem ser incluídos no código, em commits, issues ou documentação.
- Dados de pacientes e informações pessoais não devem ser enviados ao repositório.
- A saída completa de `docker compose config` pode revelar os valores do `.env`; não a publique.
- Antes de cada commit, utilize `git status` e revise o conteúdo preparado com `git diff --cached`.

## Ingestão de pacientes por CSV

O MVP 0.3.0 adiciona o primeiro fluxo de ingestão do DataLake.

O sistema lê um arquivo CSV de pacientes sintéticos, valida sua estrutura,
normaliza valores e insere apenas os registros ainda inexistentes em
`core.patients`.

### Formato esperado

```csv
external_code,birth_date,biological_sex
PAT-CSV-0001,1995-04-10,female
PAT-CSV-0002,1988-11-23,male
PAT-CSV-0003,2001-02-15,not_informed
PAT-CSV-0004,,unknown
PAT-CSV-0005,1976-08-30,
```

As três colunas devem existir. `external_code` é obrigatório em todas as
linhas; `birth_date` e `biological_sex` podem estar vazios.

Os valores permitidos para `biological_sex` são `female`, `male`, `intersex`,
`unknown`, `not_informed` ou vazio. Datas preenchidas devem usar o formato
`AAAA-MM-DD`.

### Executar a ingestão

Com o ambiente virtual ativado, o PostgreSQL saudável e as migrações aplicadas:

```powershell
docker compose up -d
python -m alembic upgrade head
python -m datalake.ingestion.cli data/examples/patients.csv
```

Exemplo de saída na primeira execução:

```text
Ingestão concluída.

Registros recebidos: 5
Registros inseridos: 5
Registros já existentes: 0
Avisos: 0
```

### Idempotência

A ingestão pode ser repetida sem duplicar pacientes. O serviço consulta
`external_code` antes da inserção, e a constraint única do PostgreSQL permanece
como proteção final.

Na segunda execução do mesmo arquivo, os cinco registros são contabilizados
como existentes e nenhum novo paciente é inserido.

### Consultar os pacientes

```powershell
docker compose exec postgres psql -U datalake_user -d datalake -c "SELECT external_code, birth_date, biological_sex FROM core.patients ORDER BY external_code;"
```

### Validações e erros

A ingestão é interrompida quando houver:

- arquivo inexistente, vazio ou malformado;
- colunas obrigatórias ausentes;
- arquivo sem registros;
- código externo vazio ou duplicado dentro do arquivo;
- data fora do formato esperado;
- valor inválido para `biological_sex`.

Falhas durante a persistência provocam rollback da transação. A CLI apresenta
mensagens compreensíveis e encerra com um código diferente de zero quando
ocorre um erro.

### Limitações atuais

- linhas inválidas são rejeitadas sem interromper o processamento das válidas;
- apenas pacientes em CSV são suportados;
- pacientes existentes não são atualizados;
- não existe staging, tabela de cargas ou hash do arquivo;
- registros rejeitados são armazenados somente em relatórios CSV locais;
- não existe API REST.

O contrato completo está documentado em
[`docs/patient-csv-ingestion.md`](docs/patient-csv-ingestion.md).

## Qualidade dos dados

O MVP 0.4.0 valida os pacientes individualmente.

Registros válidos continuam no pipeline, enquanto registros inválidos são
gravados em um relatório local na pasta `data/rejected`.

### Executar o exemplo

```powershell
python -m datalake.ingestion.cli data/examples/patients_with_quality_issues.csv
```

### Métricas

A execução apresenta:

- recebidos;
- válidos;
- rejeitados;
- inseridos;
- existentes;
- taxa de aceitação;
- avisos.

### Relatório

O relatório contém os dados originais, a linha do CSV, os códigos e as
mensagens dos problemas.

Os arquivos da pasta `data/rejected` não são versionados.

## Status do projeto

**MVP 0.4.0 — Validação e qualidade dos dados concluída.**

A plataforma separa registros válidos e inválidos, mantém o processamento dos
dados aceitos, gera relatórios locais de rejeição e apresenta métricas de
qualidade da ingestão.

**Próximo MVP:** `v0.5.0` — pipeline ETL, staging, histórico de cargas e
rastreabilidade.
