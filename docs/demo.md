# Demonstração do DataLake

## Objetivo

Este roteiro apresenta as principais capacidades do projeto em aproximadamente cinco a dez minutos.

## 1. Iniciar a plataforma

```powershell
docker compose up -d --build
docker compose ps
```

Confirme:

- PostgreSQL saudável;
- migrations concluídas;
- API saudável.

## 2. Executar uma ingestão

```powershell
python -m datalake.ingestion.cli `
  data/examples/patients_with_quality_issues.csv `
  --source-name "portfolio_demo" `
  --force
```

Observe:

- SHA-256;
- UUID da execução;
- registros recebidos;
- registros válidos;
- registros rejeitados;
- registros inseridos;
- registros existentes;
- taxa de aceitação;
- artefatos gerados.

## 3. Consultar a API

Abra a documentação interativa:

- [Swagger UI](http://localhost:8000/docs)

Teste os endpoints:

- `GET /health/live`;
- `GET /health/ready`;
- `GET /api/v1/patients`;
- `GET /api/v1/source-files`;
- `GET /api/v1/ingestion-runs`.

## 4. Consultar uma execução

Copie o UUID exibido pela CLI e acesse:

```http
GET /api/v1/ingestion-runs/{run_uuid}
```

Depois, consulte os registros e problemas de qualidade:

```http
GET /api/v1/ingestion-runs/{run_uuid}/records
GET /api/v1/ingestion-runs/{run_uuid}/quality-issues
```

## 5. Demonstrar lineage

Escolha um registro de staging e acesse:

```http
GET /api/v1/staged-records/{record_id}/lineage
```

Explique a ligação:

```text
fonte → arquivo → execução → linha → paciente ou problema
```

## 6. Demonstrar idempotência

Execute novamente o mesmo arquivo sem `--force`:

```powershell
python -m datalake.ingestion.cli `
  data/examples/patients_with_quality_issues.csv `
  --source-name "portfolio_demo"
```

O status esperado é:

```text
skipped_duplicate
```

## 7. Demonstrar testes

```powershell
python -m pytest
```

## 8. Demonstrar cobertura

```powershell
python -m pytest `
  --cov=datalake `
  --cov-branch `
  --cov-report=term-missing
```

## 9. Demonstrar CI

Abra a aba **Actions** no GitHub e mostre:

- o job `Quality`;
- o job `Tests and coverage`;
- o job `Docker build`;
- os artifacts gerados.
