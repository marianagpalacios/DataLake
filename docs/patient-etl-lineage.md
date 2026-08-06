# Pipeline ETL e rastreabilidade de pacientes

## 1. Objetivo

Este documento descreve o pipeline ETL de pacientes implementado no
MVP 0.5.0.

O pipeline preserva o arquivo recebido, calcula sua identidade por SHA-256,
registra cada tentativa de processamento, armazena as linhas em staging,
persiste os problemas de qualidade e mantém a relação entre fonte,
execução, registro intermediário e paciente.

## 2. Etapas

### 2.1 Extract

- localizar o arquivo;
- calcular SHA-256;
- registrar tamanho e nome;
- copiar o arquivo para `data/raw`;
- registrar a fonte e o arquivo no PostgreSQL.

### 2.2 Transform

- ler o CSV;
- verificar a estrutura;
- validar cada linha;
- normalizar registros válidos;
- classificar registros rejeitados;
- gerar artefatos processados e rejeitados.

### 2.3 Load

- inserir todas as linhas em staging;
- inserir pacientes válidos e novos no core;
- persistir problemas no schema quality;
- atualizar as métricas da execução.

## 3. Identidade do arquivo

A identidade utiliza a combinação:

`data_source_id + sha256`

## 4. Status

- `running`;
- `completed`;
- `completed_with_rejections`;
- `failed`;
- `skipped_duplicate`.

## 5. Schemas

- `ingestion`: arquivos e execuções;
- `staging`: registros intermediários;
- `quality`: problemas de qualidade;
- `core`: dados confiáveis.

## 6. Rastreabilidade

A cadeia será:

`DataSource -> SourceFile -> IngestionRun -> StagedPatientRecord`

Registros válidos poderão apontar para `core.patients`.

Registros rejeitados possuirão itens em
`quality.data_quality_issues`.

## 7. Arquivos locais

- `data/raw`: cópia imutável do arquivo recebido;
- `data/processed`: registros válidos normalizados;
- `data/rejected`: relatório dos registros rejeitados.

Esses diretórios permanecem ignorados pelo Git.

## 8. Duplicidades

Arquivos já processados serão marcados como `skipped_duplicate`.

A opção `--force` permitirá um reprocessamento consciente.

## 9. Falhas

Falhas ocorridas após o registro da execução deverão atualizar seu status
para `failed` e armazenar uma mensagem resumida.

## 10. Limitações

- apenas pacientes em CSV;
- armazenamento local de arquivos;
- sem execução assíncrona;
- sem API;
- sem armazenamento em S3 ou MinIO;
- sem atualização de pacientes existentes.