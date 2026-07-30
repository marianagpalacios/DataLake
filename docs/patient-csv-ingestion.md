# Ingestão de pacientes por CSV

## Objetivo

O MVP 0.3.0 introduz a primeira entrada de dados externos no DataLake. O
processo recebe um arquivo CSV com pacientes sintéticos ou pseudonimizados,
realiza validações básicas e insere os novos registros na tabela
`core.patients` do PostgreSQL por meio do SQLAlchemy.

Este fluxo tem como objetivos:

- estabelecer um contrato simples para arquivos de entrada;
- separar leitura, validação, transformação e persistência;
- impedir duplicidades simples por código externo;
- executar a gravação em uma transação;
- apresentar um resumo da execução;
- permitir testes unitários e de integração.

Somente dados sintéticos, fictícios, públicos ou adequadamente anonimizados
podem ser utilizados. Arquivos com dados pessoais ou clínicos reais não devem
ser adicionados ao repositório.

## Formato esperado do CSV

O arquivo deve:

- utilizar o formato CSV;
- possuir uma linha de cabeçalho;
- usar vírgula como separador;
- estar codificado em UTF-8;
- conter as três colunas obrigatórias;
- possuir uma linha para cada paciente.

Exemplo:

```csv
external_code,birth_date,biological_sex
PAT-0001,1995-04-10,female
PAT-0002,1988-11-23,male
PAT-0003,2001-02-15,not_informed
```

Colunas adicionais serão permitidas neste MVP, mas serão ignoradas durante o
mapeamento. O arquivo de exemplo do projeto ficará em
`data/examples/patients.csv` e conterá somente dados fictícios.

## Colunas obrigatórias

| Coluna | Tipo esperado | Obrigatória no cabeçalho | Valor vazio permitido |
| --- | --- | --- | --- |
| `external_code` | texto com até 50 caracteres | sim | não |
| `birth_date` | data no formato `AAAA-MM-DD` | sim | sim |
| `biological_sex` | texto normalizado | sim | sim |

### `external_code`

Identifica o paciente no sistema de origem.

Regras:

- deve estar presente e não pode ser vazio;
- espaços no início e no fim serão removidos;
- deve possuir no máximo 50 caracteres;
- deve ser único dentro do arquivo;
- deve ser único na tabela `core.patients`;
- letras maiúsculas e minúsculas não serão convertidas automaticamente.

### `birth_date`

Representa a data de nascimento do paciente.

Regras:

- deve utilizar o formato ISO `AAAA-MM-DD` quando preenchida;
- será convertida para um objeto `date` do Python;
- um valor vazio será convertido para `NULL`;
- valores que não puderem ser interpretados como data serão rejeitados.

### `biological_sex`

Representa o sexo biológico informado pelo sistema de origem.

Regras:

- espaços no início e no fim serão removidos;
- o texto será convertido para letras minúsculas;
- um valor vazio será convertido para `NULL`;
- quando preenchido, deve corresponder a um dos valores permitidos.

## Valores permitidos

Os valores aceitos para `biological_sex` são:

| Valor | Significado |
| --- | --- |
| `female` | feminino |
| `male` | masculino |
| `intersex` | intersexo |
| `unknown` | desconhecido |
| `not_informed` | não informado |

Esses valores correspondem à restrição
`core.patients.biological_sex_allowed` existente no banco de dados.

## Fluxo de ingestão

O processamento seguirá estas etapas:

```text
Arquivo CSV
    |
    v
Leitura com Pandas
    |
    v
Validação básica do arquivo e dos registros
    |
    v
Normalização e mapeamento para objetos Patient
    |
    v
Consulta dos códigos externos já existentes
    |
    v
Inserção em lote dos pacientes novos
    |
    v
Commit da transação e resumo da execução
```

Cada componente possuirá uma responsabilidade específica:

- o leitor verificará o caminho, abrirá o CSV e retornará um `DataFrame`;
- o validador verificará a estrutura e as regras básicas dos dados;
- o mapper converterá cada linha validada em um objeto `Patient`;
- o serviço coordenará o processo, consultará duplicidades, controlará a
  transação e produzirá o resumo.

Uma falha antes da conclusão da gravação provocará rollback. O processo não
deverá deixar uma carga parcialmente persistida.

## Comportamento diante de duplicidades

### Duplicidades no mesmo arquivo

Mais de uma linha com o mesmo `external_code` será considerada erro de
validação. Neste MVP, o arquivo será rejeitado antes de qualquer inserção.

### Registros existentes no banco

Quando um `external_code` já estiver presente em `core.patients`, o registro
será contado como existente e não será inserido ou atualizado.

A restrição `UNIQUE` do banco continua sendo a proteção final, mas o serviço
consultará previamente os códigos existentes. Assim, repetir a mesma ingestão
não criará novos pacientes.

Exemplo:

```text
Primeira execução: 3 recebidos, 3 inseridos, 0 existentes
Segunda execução: 3 recebidos, 0 inseridos, 3 existentes
```

Esse comportamento fornece idempotência básica por `external_code`. Uma
alteração em outros campos de um paciente já existente não será aplicada neste
MVP.

## Erros previstos

O processo deverá apresentar mensagens compreensíveis para os seguintes casos:

### Erros de leitura

- caminho inexistente;
- caminho que aponta para um diretório;
- arquivo vazio;
- arquivo sem cabeçalho;
- conteúdo CSV malformado;
- codificação incompatível;
- falta de permissão para leitura.

### Erros de validação

- ausência de uma ou mais colunas obrigatórias;
- `external_code` vazio ou acima do limite permitido;
- `external_code` duplicado dentro do arquivo;
- `birth_date` inválida;
- `biological_sex` fora dos valores permitidos.

### Erros de ingestão

- indisponibilidade ou falha de conexão com o PostgreSQL;
- violação de uma restrição do banco;
- falha durante a inserção ou o commit;
- erro inesperado durante o processamento.

Erros de validação interromperão a ingestão do arquivo inteiro. Erros de banco
provocarão rollback da transação. O armazenamento detalhado de registros
rejeitados será implementado em um MVP posterior.

## Forma de execução

A interface de linha de comando será executada a partir da raiz do projeto:

```powershell
python -m datalake.ingestion.cli data/examples/patients.csv
```

Antes da primeira execução, o PostgreSQL deve estar ativo e com as migrações
aplicadas:

```powershell
docker compose up -d
python -m alembic upgrade head
```

## Exemplos de execução

### Primeira ingestão

```text
Arquivo: data/examples/patients.csv
Registros recebidos: 3
Registros inseridos: 3
Registros já existentes: 0
Status: concluído
```

### Reexecução do mesmo arquivo

```text
Arquivo: data/examples/patients.csv
Registros recebidos: 3
Registros inseridos: 0
Registros já existentes: 3
Status: concluído
```

### Falha de validação

```text
Arquivo: data/examples/patients.csv
Status: falhou
Erro: coluna obrigatória ausente: birth_date
```

Após uma execução bem-sucedida, os dados poderão ser conferidos com:

```sql
SELECT
    id,
    external_code,
    birth_date,
    biological_sex
FROM core.patients
ORDER BY external_code;
```

## Limitações do MVP 0.3.0

Este MVP não contempla:

- ingestão de exames, amostras ou outras entidades;
- formatos de entrada diferentes de CSV;
- escolha automática de separador ou codificação;
- atualização de pacientes já existentes;
- rejeição parcial de linhas inválidas;
- correção automática de valores;
- armazenamento dos registros rejeitados;
- staging no PostgreSQL;
- registro persistente de cada execução;
- identificação de arquivos por hash;
- métricas avançadas de qualidade;
- processamento de arquivos muito grandes ou em partes;
- API REST, interface gráfica ou autenticação.

Validação detalhada, classificação de registros válidos e inválidos e
relatórios de qualidade pertencem ao MVP 0.4.0. Staging, rastreabilidade e
controle formal das execuções pertencem ao MVP 0.5.0.
