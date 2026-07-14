# DataLake

## Sobre o projeto

O DataLake é uma plataforma educacional de engenharia de dados em saúde. O projeto simula, em menor escala, os desafios encontrados na integração de informações produzidas por laboratórios, clínicas, hospitais, instituições de pesquisa e outros sistemas de saúde.

Nesta primeira versão, o foco está na criação de uma base de desenvolvimento profissional, organizada e reproduzível. O MVP 0.1.0 entrega um projeto Python instalável e um banco de dados PostgreSQL executado com Docker Compose.

> O projeto utiliza somente dados sintéticos, fictícios, públicos ou adequadamente anonimizados. Dados clínicos reais e informações pessoais não devem ser adicionados ao repositório.

## Problema

Sistemas de saúde podem representar informações equivalentes com nomes, estruturas, formatos, códigos e unidades diferentes. Essas diferenças dificultam a consolidação, a validação e a análise conjunta dos dados, além de prejudicarem a identificação de sua origem e das transformações aplicadas durante o processamento.

Sem um fluxo padronizado e rastreável, podem surgir registros duplicados, valores inválidos, informações incompletas, falhas silenciosas e perda da relação entre o dado armazenado e sua fonte.

## Objetivo

O objetivo do projeto é desenvolver progressivamente uma plataforma capaz de receber, validar, transformar, armazenar e disponibilizar dados de saúde de maneira segura, organizada e rastreável.

No MVP 0.1.0, o objetivo específico é garantir que outra pessoa autorizada consiga clonar o repositório, configurar o ambiente local, instalar o pacote Python, iniciar o PostgreSQL, verificar a saúde do serviço e conectar-se ao banco.

A visão completa do produto está documentada em [`docs/project-vision.md`](docs/project-vision.md).

## Arquitetura atual

```text
┌───────────────────────────┐
│     Projeto DataLake      │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│      Docker Compose       │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│        PostgreSQL         │
│ Banco: datalake           │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│    Volume persistente     │
└───────────────────────────┘
```

O Docker Compose declara o serviço PostgreSQL e torna a infraestrutura reproduzível. O health check utiliza `pg_isready` para confirmar que o banco está aceitando conexões, enquanto o volume nomeado preserva os dados quando o contêiner é recriado.

## Tecnologias

- Python 3.12 ou superior;
- PostgreSQL 17;
- Docker Desktop;
- Docker Compose;
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
py -3.12 -m venv .venv
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
python -m pip install -e .
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

### 6. Verificar o serviço

```powershell
docker compose ps
```

Após alguns segundos, o serviço deverá aparecer como `healthy`. Se aparecer `health: starting`, aguarde e execute o comando novamente.

Para consultar os logs:

```powershell
docker compose logs postgres
```

### 7. Conectar-se ao banco

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

> Não execute `docker compose down -v` sem compreender o impacto. A opção `-v` remove o volume e apaga os dados armazenados no PostgreSQL.

## Estrutura de diretórios

```text
DataLake/
├── data/
│   ├── processed/
│   │   └── .gitkeep
│   ├── raw/
│   │   └── .gitkeep
│   └── rejected/
│       └── .gitkeep
├── docs/
│   └── project-vision.md
├── src/
│   └── datalake/
│       └── __init__.py
├── tests/
│   └── .gitkeep
├── .editorconfig
├── .env.example
├── .gitignore
├── compose.yaml
├── pyproject.toml
└── README.md
```

- `data/raw`: dados recebidos sem transformação;
- `data/processed`: dados processados e aceitos;
- `data/rejected`: dados rejeitados durante validações futuras;
- `docs`: documentação do produto e da arquitetura;
- `src/datalake`: código-fonte do pacote Python;
- `tests`: testes automatizados que serão adicionados progressivamente.

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

**MVP 0.1.0 — Infraestrutura inicial em desenvolvimento.**

A estrutura Python e a infraestrutura local do PostgreSQL estão funcionais. O banco inicia com Docker Compose, apresenta estado `healthy`, aceita consultas SQL e utiliza um volume persistente. A entrega será concluída após revisão, Pull Request, integração na branch `main`, criação da tag `v0.1.0` e publicação da release correspondente.
