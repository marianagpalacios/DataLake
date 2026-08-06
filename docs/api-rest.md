# API REST do DataLake

## 1. Objetivo

A API REST disponibiliza consultas controladas aos dados processados pelo
DataLake sem expor acesso direto ao PostgreSQL.

## 2. Escopo

A versão `v0.6.0` é somente leitura.

A ingestão de arquivos continua sendo realizada pela interface de linha de
comando.

## 3. Prefixo

Os recursos da primeira versão utilizam:

`/api/v1`

## 4. Saúde

- `GET /health/live`;
- `GET /health/ready`.

## 5. Pacientes

- `GET /api/v1/patients`;
- `GET /api/v1/patients/{patient_id}`.

Filtros:

- `external_code`;
- `biological_sex`.

## 6. Arquivos

- `GET /api/v1/source-files`;
- `GET /api/v1/source-files/{source_file_id}`.

Filtros:

- `data_source_id`;
- `original_name`;
- `sha256`.

## 7. Execuções

- `GET /api/v1/ingestion-runs`;
- `GET /api/v1/ingestion-runs/{run_uuid}`;
- `GET /api/v1/ingestion-runs/{run_uuid}/records`;
- `GET /api/v1/ingestion-runs/{run_uuid}/quality-issues`.

## 8. Lineage

- `GET /api/v1/staged-records/{record_id}/lineage`.

## 9. Paginação

Parâmetros:

- `page`, com valor mínimo `1`;
- `size`, entre `1` e `100`.

## 10. Campos não expostos

A API não publica diretamente:

- caminhos internos dos arquivos;
- registros brutos completos;
- valores brutos dos erros;
- mensagens técnicas internas;
- credenciais;
- senhas.

## 11. Status HTTP

- `200`: sucesso;
- `404`: recurso inexistente;
- `422`: parâmetros inválidos;
- `503`: banco indisponível.

## 12. Documentação automática

- Swagger UI: `/docs`;
- ReDoc: `/redoc`;
- OpenAPI: `/openapi.json`.

## 13. Limitações

- sem autenticação;
- sem autorização;
- sem upload;
- sem criação ou atualização de pacientes;
- sem CORS para frontend externo;
- sem rate limiting;
- sem cache;
- sem execução assíncrona de pipelines.