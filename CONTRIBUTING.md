# Como contribuir com o DataLake

## 1. Escopo

O DataLake é um projeto educacional de engenharia de dados em saúde.

Utilize somente dados sintéticos ou públicos que possam ser legalmente
incluídos no repositório.

## 2. Preparar o ambiente

```powershell
git clone https://github.com/marianagpalacios/DataLake.git
cd DataLake

python -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1

python -m pip install -e ".[dev]"
```

## 3. Banco de desenvolvimento

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

##  4. Banco de testes

```powershell
Copy-Item .env.test.example .env.test

docker compose `
  --env-file .env.test `
  -f compose.test.yaml `
  up -d
```

## 5. Criar uma branch

Utilize nomes descritivos:

- feature/...;
- fix/...;
- docs/...;
- test/...;
- refactor/....

##  6. Validar antes do push
- python -m ruff format --check src tests
- python -m ruff check src tests
- python -m pytest
- python -m compileall src tests

##  7. Commits

Exemplos:

- feat(api): add endpoint;
- fix(pipeline): prevent duplicate processing;
- test(api): cover invalid pagination;
- docs: update architecture;
- ci: improve workflow.

##  8. Pull Request

Explique:

- objetivo;
- alterações;
- como validar;
- impactos;
- limitações.

## 9. Dados sensíveis

Nunca envie:

- nomes reais;
- CPF;
- prontuários;
- endereços;
- telefones;
- dados genômicos identificáveis;
- credenciais;
- tokens;
- arquivos .env.