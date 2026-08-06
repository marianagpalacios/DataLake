# DataLake

## Sobre o projeto

O DataLake é uma plataforma educacional de engenharia de dados em saúde. O projeto simula, em menor escala, desafios encontrados na integração de informações produzidas por laboratórios, clínicas, hospitais, instituições de pesquisa e outros sistemas de saúde.

A versão atual, v0.5.0, transforma a ingestão de pacientes em um pipeline ETL rastreável. O sistema identifica cada arquivo por SHA-256, preserva uma cópia na camada raw, registra as execuções no PostgreSQL e mantém em staging tanto os registros válidos quanto os rejeitados.

Os pacientes válidos e ainda inexistentes são inseridos no schema `core`. Os problemas encontrados são persistidos no schema `quality`, e os artefatos processados e rejeitados são gravados localmente. Cada execução preserva sua origem, métricas, status e relação com eventuais processamentos anteriores do mesmo arquivo.

O projeto utiliza somente dados sintéticos, fictícios, públicos ou adequadamente anonimizados. Dados clínicos reais e informações pessoais não devem ser adicionados ao repositório.

## Problema

Sistemas de saúde podem representar informações equivalentes com nomes, estruturas, formatos, códigos e unidades diferentes. Essas diferenças dificultam a consolidação, a validação e a análise conjunta dos dados, além de prejudicarem a identificação de sua origem e das transformações aplicadas durante o processamento.

Sem um fluxo padronizado e rastreável, podem surgir registros duplicados, valores inválidos, informações incompletas, falhas silenciosas e perda da relação entre o dado armazenado e sua fonte.

## Objetivo

O objetivo do projeto é desenvolver progressivamente uma plataforma capaz de receber, validar, transformar, armazenar e disponibilizar dados de saúde de maneira segura, organizada e rastreável.

No MVP 0.5.0, o objetivo específico é tornar a ingestão rastreável de ponta a ponta por meio de:

- preservação do arquivo original na camada raw;

- validação linha a linha;

- identificação determinística por SHA-256;

- registro do histórico e do status das execuções;

- persistência de todas as linhas no schema `staging`;

- persistência dos problemas no schema `quality`;

- detecção de arquivos já processados e reprocessamento explícito;

- carga transacional dos pacientes válidos e ainda inexistentes no schema `core`.

A visão completa do produto está documentada em [`docs/project-vision.md`](docs/project-vision.md).

## Arquitetura atual

```text
Arquivo CSV
    |
    v
Preparação do arquivo + SHA-256
    |
    v
Camada raw (data/raw)
    |
    v
ingestion.data_sources
ingestion.source_files
ingestion.ingestion_runs (running)
    |
    v
Leitura + validação estrutural e linha a linha
    |
    +--------------------------+--------------------------+
    |                          |                          |
    v                          v                          v
staging.patient_records   quality.data_quality_issues  Artefatos CSV
(válidos e rejeitados)    (problemas por campo)        processed/rejected
    |
    v
Mapeamento e carga
    |
    v
core.patients
    |
    v
ingestion.ingestion_runs
(completed, completed_with_rejections, failed
ou skipped_duplicate)
```

As configurações são carregadas do arquivo `.env`. Antes da leitura, o arquivo recebe uma identificação SHA-256 e uma cópia é preservada em `data/raw`. A fonte, o arquivo e a tentativa de processamento são registrados no schema `ingestion`.

Quando a estrutura é válida, cada linha é analisada separadamente e persistida em `staging.patient_records` com seu número original, conteúdo bruto, valores normalizados e resultado da validação. Os problemas são armazenados em `quality.data_quality_issues`.

O serviço consulta os códigos externos já armazenados, insere somente os pacientes válidos e novos em `core.patients` e relaciona o staging ao registro final. A transação é controlada pelo SQLAlchemy: falhas na persistência provocam rollback e a execução é marcada como `failed`.

Os relatórios de rejeição são arquivos locais em `data/rejected` e não são versionados. Eles preservam os dados originais da linha, o número da linha no CSV, os campos afetados, os códigos dos erros e as mensagens explicativas.

O Alembic cria e versiona a estrutura do banco. O schema `ingestion` mantém fontes, arquivos e execuções; `staging` preserva as linhas recebidas; `quality` registra os problemas de qualidade; e `core` concentra os dados tratados do domínio.

O Docker Compose declara o serviço PostgreSQL e torna a infraestrutura reproduzível. O health check utiliza pg_isready para confirmar que o banco está aceitando conexões, enquanto o volume nomeado preserva os dados quando o contêiner é recriado.

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

Importe o arquivo sintético sem problemas de qualidade:

```powershell
python -m datalake.ingestion.cli data/examples/patients.csv
```

Exemplo de saída em um banco no qual os pacientes ainda não existem:

```text
Ingestão concluída.

Execução: <uuid>
Status: completed
Arquivo: C:\...\DataLake\data\examples\patients.csv
SHA-256: <sha256>
Camada raw: C:\...\DataLake\data\raw\<hash>_patients.csv
Arquivo processado: C:\...\DataLake\data\processed\patients_processed_<uuid>.csv
Registros recebidos: 5
Registros válidos: 5
Registros rejeitados: 0
Registros inseridos: 5
Registros já existentes: 0
Taxa de aceitação: 100.00%
Avisos: 0
```

Para demonstrar o sucesso parcial e os relatórios de rejeição, execute:

```powershell
python -m datalake.ingestion.cli data/examples/patients_with_quality_issues.csv
```

Exemplo de saída em um banco limpo para os códigos `PAT-QA-*`:

```text
Ingestão concluída.

Execução: <uuid>
Status: completed_with_rejections
Arquivo: C:\...\DataLake\data\examples\patients_with_quality_issues.csv
SHA-256: <sha256>
Camada raw: C:\...\DataLake\data\raw\<hash>_patients_with_quality_issues.csv
Arquivo processado: C:\...\DataLake\data\processed\patients_with_quality_issues_processed_<uuid>.csv
Relatório de rejeições: C:\...\DataLake\data\rejected\patients_with_quality_issues_rejected_<timestamp>.csv
Registros recebidos: 9
Registros válidos: 3
Registros rejeitados: 6
Registros inseridos: 3
Registros já existentes: 0
Taxa de aceitação: 33.33%
Avisos: 3
```

O número de registros inseridos e já existentes varia conforme o conteúdo atual do banco. A quantidade de registros válidos, rejeitados e a taxa de aceitação dependem somente do arquivo processado.

As pastas e o nome lógico da fonte podem ser alterados pela CLI:

```powershell
python -m datalake.ingestion.cli data/examples/patients_with_quality_issues.csv `
    --source-name laboratorio_demo `
    --raw-dir temp/raw `
    --processed-dir temp/processed `
    --rejected-dir temp/rejected
```

Por padrão, um arquivo com o mesmo SHA-256 e a mesma fonte que já tenha sido concluído não é processado novamente. A nova tentativa recebe o status `skipped_duplicate` e aponta para a execução original. Para reprocessar intencionalmente o conteúdo e criar uma nova execução e um novo staging, utilize:

```powershell
python -m datalake.ingestion.cli data/examples/patients.csv --force
```

### 9. Executar os testes

```powershell
python -m pytest
```

Para executar somente os testes unitários:

```powershell
python -m pytest -m "not integration"
```

A suíte atual contém 35 testes distribuídos entre configurações, modelos, arquivos do pipeline, leitura de CSV, mapeamento, validação linha a linha, artefatos, relatórios e integração ETL com o PostgreSQL.

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

Para sair do psql:

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

Não execute `docker compose down -v` sem compreender o impacto. A opção `-v` remove o volume e apaga os dados armazenados no PostgreSQL.

## Estrutura de diretórios

```text
DataLake/
├── alembic/
│   ├── versions/
│   │   ├── *_create_initial_database_schema.py
│   │   └── *_add_etl_lineage_and_staging.py
│   ├── README
│   ├── env.py
│   └── script.py.mako
├── data/
│   ├── examples/
│   │   ├── patients.csv
│   │   └── patients_with_quality_issues.csv
│   ├── processed/
│   │   └── .gitkeep
│   ├── raw/
│   │   └── .gitkeep
│   └── rejected/
│       └── .gitkeep
├── docs/
│   ├── database-model.md
│   ├── patient-csv-ingestion.md
│   ├── patient-data-quality.md
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
│       │   ├── biological_sample.py
│       │   ├── data_quality_issue_record.py
│       │   ├── data_source.py
│       │   ├── exam_result.py
│       │   ├── exam_type.py
│       │   ├── ingestion_run.py
│       │   ├── laboratory_exam.py
│       │   ├── patient.py
│       │   ├── source_file.py
│       │   └── staged_patient_record.py
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── artifacts.py
│       │   ├── exceptions.py
│       │   ├── files.py
│       │   └── patient_etl.py
│       ├── quality/
│       │   ├── __init__.py
│       │   ├── exceptions.py
│       │   ├── models.py
│       │   └── reports.py
│       └── __init__.py
├── tests/
│   ├── integration/
│   │   ├── test_database_connection.py
│   │   ├── test_patient_etl.py
│   │   └── test_patient_ingestion.py
│   └── unit/
│       ├── ingestion/
│       │   ├── test_csv_reader.py
│       │   ├── test_patient_mapper.py
│       │   └── test_patient_validator.py
│       ├── quality/
│       │   └── test_rejection_report.py
│       ├── pipeline/
│       │   ├── test_artifacts.py
│       │   └── test_files.py
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

- `data/examples`:  arquivos sintéticos seguros para demonstração;

- `data/raw`: área reservada para arquivos recebidos sem transformação;

- `data/processed`: área reservada para dados processados e aceitos;

- `data/rejected`: recebe relatórios CSV locais com registros rejeitados; seu conteúdo permanece ignorado pelo Git;

- `docs`: documentação do produto, banco, ingestão e qualidade dos dados;

- `src/datalake/config`: carregamento e validação das configurações;

- `src/datalake/database`: base declarativa, conexão e sessões do banco;

- `src/datalake/ingestion`: leitura, validação, mapeamento, serviço e CLI;

- `src/datalake/models`: modelos SQLAlchemy do domínio;

- `src/datalake/pipeline`: preparação de arquivos, geração de artefatos e orquestração do ETL;

- `src/datalake/quality`: representação dos problemas de qualidade e geração de relatórios de rejeição;

- `alembic`: configuração e versões das migrações;

- `tests`: testes unitários e de integração.

Os diretórios `raw`, `processed` e `rejected` mantêm somente arquivos `.gitkeep` no Git. Seu conteúdo local é ignorado para reduzir o risco de exposição acidental de dados sensíveis. A camada raw preserva a cópia identificada pelo hash do arquivo; `processed` recebe os registros normalizados aceitos; e `rejected` recebe os relatórios locais. Apenas arquivos sintéticos preparados para demonstração podem ser versionados em `data/examples`.

## Roadmap

- [x] MVP 0.1.0 — infraestrutura, Docker e PostgreSQL;

- [x] MVP 0.2.0 — modelagem, SQLAlchemy e Alembic;

- [x] MVP 0.3.0 — primeira ingestão de pacientes por CSV;

- [x] MVP 0.4.0 — validação e qualidade dos dados;

- [x] MVP 0.5.0 — pipeline ETL, staging e rastreabilidade;

- [ ] MVP 0.6.0 — API REST com FastAPI;

- [ ] MVP 0.7.0 — testes completos e banco de testes;

- [ ] MVP 0.8.0 — GitHub Actions e preparação do portfólio.

## Segurança e dados

- O arquivo .env contém configurações locais e nunca deve ser versionado.

- O .env.example serve apenas como modelo e não deve conter senhas reais.

- Senhas, tokens e outras credenciais não devem ser incluídos no código, em commits, issues ou documentação.

- Dados de pacientes e informações pessoais não devem ser enviados ao repositório.

- A saída completa de docker compose config pode revelar os valores do .env; não a publique.

- Antes de cada commit, utilize git status e revise o conteúdo preparado com git diff --cached.

## Ingestão de pacientes por CSV

O MVP 0.3.0 criou o primeiro fluxo de ingestão do DataLake: leitura com Pandas, validação do contrato, normalização, mapeamento para Patient, persistência transacional e idempotência por `external_code`.

O MVP 0.4.0 ampliou esse fluxo com validação individual, sucesso parcial, registros rejeitados estruturados, relatórios CSV locais e métricas de qualidade. Portanto, as regras descritas abaixo representam o comportamento atual.

O MVP 0.5.0 adiciona a preparação do arquivo, camada raw, identificação por SHA-256, histórico de execuções, staging por linha, problemas de qualidade persistidos e ligação entre o dado recebido e o paciente armazenado em `core`.

### Formato esperado

```csv
external_code,birth_date,biological_sex
PAT-CSV-0001,1995-04-10,female
PAT-CSV-0002,1988-11-23,male
PAT-CSV-0003,2001-02-15,not_informed
PAT-CSV-0004,,unknown
PAT-CSV-0005,1976-08-30,
```

As três colunas devem existir. `external_code` é obrigatório em todas as linhas; `birth_date` e `biological_sex` podem estar vazios.

Os valores permitidos para `biological_sex` são `female`, `male`, `intersex`, `unknown`, `not_informed` ou vazio. Datas preenchidas devem usar o formato `AAAA-MM-DD` e não podem estar no futuro.

### Idempotência

A ingestão pode ser repetida sem duplicar pacientes. O serviço consulta `external_code` antes da inserção, e a constraint única do PostgreSQL permanece como proteção final.

Pacientes válidos que já existam são contabilizados em Registros já existentes, mas não são atualizados nem inseridos novamente.

Além dessa idempotência no domínio, o ETL evita repetir o processamento do mesmo conteúdo. Um SHA-256 já concluído para a mesma fonte gera uma execução `skipped_duplicate`. Use `--force` quando precisar criar deliberadamente uma nova execução e um novo staging para o arquivo.

### Consultar os pacientes

```powershell
docker compose exec postgres psql -U datalake_user -d datalake -c "SELECT external_code, birth_date, biological_sex FROM core.patients ORDER BY external_code;"
```

### Validações e erros

Os erros são divididos em duas categorias.

### Erros estruturais bloqueantes

Impedem a interpretação segura do arquivo e interrompem a execução:

- arquivo inexistente;

- arquivo vazio ou malformado;

- colunas obrigatórias ausentes;

- arquivo sem registros.

A CLI encerra com código diferente de zero nesses casos.

### Erros de conteúdo por linha

Rejeitam somente os registros afetados e não interrompem o processamento dos registros válidos:

- código externo vazio;

- código externo duplicado dentro do arquivo;

- data em formato inválido;

- data de nascimento futura;

- valor inválido para biological_sex.

Quando um código aparece mais de uma vez no mesmo arquivo, todas as ocorrências são rejeitadas, pois o sistema não escolhe arbitrariamente qual registro seria o correto.

Falhas durante a persistência dos registros válidos provocam rollback da transação.

### Relatórios de rejeição

Quando existirem registros inválidos, a execução cria um CSV local em `data/rejected`. O relatório contém:

- os campos originais do arquivo;

- o número original da linha;

- os códigos dos problemas;

- os campos afetados;

- as mensagens explicativas.

Os relatórios são ignorados pelo Git e não são armazenados no PostgreSQL nesta versão.

## Rastreabilidade do ETL

Cada tentativa de processamento recebe um UUID e um dos seguintes status:

- `running`: execução registrada e ainda não finalizada;

- `completed`: execução concluída sem rejeições;

- `completed_with_rejections`: execução concluída com sucesso parcial;

- `failed`: falha estrutural, de artefato ou de persistência;

- `skipped_duplicate`: arquivo já concluído anteriormente e ignorado sem criar um novo staging.

O arquivo é identificado pelo par fonte e SHA-256. O argumento `--force` ignora somente a decisão de pular um arquivo já concluído: ele cria uma nova execução e novos registros de staging, mas não duplica pacientes que já existam em `core.patients`.

Conecte-se ao PostgreSQL para consultar a linhagem:

```powershell
docker compose exec postgres psql -U datalake_user -d datalake
```

Execuções e arquivos de origem:

```sql
SELECT
    ir.run_uuid,
    ir.status,
    ir.pipeline_version,
    sf.original_name,
    sf.sha256,
    ir.received_count,
    ir.valid_count,
    ir.rejected_count,
    ir.inserted_count,
    ir.existing_count,
    ir.started_at,
    ir.finished_at
FROM ingestion.ingestion_runs ir
JOIN ingestion.source_files sf
    ON sf.id = ir.source_file_id
ORDER BY ir.id;
```

Linhas preservadas no staging:

```sql
SELECT
    ir.run_uuid,
    spr.source_row_number,
    spr.validation_status,
    spr.normalized_external_code,
    spr.patient_id,
    spr.raw_record
FROM staging.patient_records spr
JOIN ingestion.ingestion_runs ir
    ON ir.id = spr.ingestion_run_id
ORDER BY ir.id, spr.source_row_number;
```

Problemas de qualidade:

```sql
SELECT
    ir.run_uuid,
    spr.source_row_number,
    dqi.field,
    dqi.code,
    dqi.message,
    dqi.raw_value
FROM quality.data_quality_issues dqi
JOIN staging.patient_records spr
    ON spr.id = dqi.staged_record_id
JOIN ingestion.ingestion_runs ir
    ON ir.id = spr.ingestion_run_id
ORDER BY ir.id, spr.source_row_number, dqi.id;
```

Relação entre staging e core:

```sql
SELECT
    ir.run_uuid,
    spr.source_row_number,
    spr.normalized_external_code,
    p.id AS patient_id,
    p.external_code
FROM staging.patient_records spr
JOIN ingestion.ingestion_runs ir
    ON ir.id = spr.ingestion_run_id
LEFT JOIN core.patients p
    ON p.id = spr.patient_id
WHERE spr.validation_status = 'valid'
ORDER BY ir.id, spr.source_row_number;
```

### Limitações atuais

- apenas pacientes em CSV são processados;

- pacientes existentes não são atualizados;

- apenas o pipeline de pacientes em CSV possui staging e rastreabilidade;

- a camada raw usa o sistema de arquivos local e não possui armazenamento de objetos;

- os artefatos processados e rejeitados não são registrados como entidades próprias no banco;

- arquivos são considerados duplicados somente dentro da mesma fonte lógica;

- execuções interrompidas abruptamente podem permanecer com status `running`;

- relatórios de rejeição são somente locais;

- não há API REST.

O contrato inicial está documentado em [`docs/patient-csv-ingestion.md`](docs/patient-csv-ingestion.md), e as regras atuais de qualidade estão em [`docs/patient-data-quality.md`](docs/patient-data-quality.md).

## Qualidade dos dados

O MVP 0.4.0 introduziu as dimensões de completude, validade, unicidade e consistência temporal na ingestão de pacientes. O MVP 0.5.0 preserva os resultados dessas verificações no staging e no schema `quality`, vinculados à execução responsável.

A execução apresenta:

- status `running`, `completed`, `completed_with_rejections`, `failed` ou `skipped_duplicate`;

- arquivo processado;

- UUID da execução, SHA-256 e caminho da cópia raw;

- registros recebidos;

- registros válidos;

- registros rejeitados;

- registros inseridos;

- registros já existentes;

- taxa de aceitação;

- avisos de normalização;

- caminho do relatório, quando houver rejeições.

A taxa de aceitação é calculada com base nos registros que passaram pelas regras de conteúdo. Pacientes válidos já existentes continuam sendo considerados válidos, embora não sejam inseridos novamente.

## Status do projeto

**MVP 0.5.0 — Pipeline ETL, staging e rastreabilidade concluído.**

A plataforma identifica arquivos por SHA-256, preserva cópias na camada raw,
registra execuções no PostgreSQL, mantém todas as linhas em staging, persiste
problemas de qualidade e relaciona os registros aceitos aos pacientes do core.

**Próximo MVP:** `v0.6.0` — API REST com FastAPI.
