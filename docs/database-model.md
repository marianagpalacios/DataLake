# Modelo Inicial do Banco de Dados

## 1. Objetivo

Este documento descreve o modelo inicial do banco de dados da plataforma DataLake. O modelo organiza dados sintéticos de saúde relacionados a pacientes pseudonimizados, amostras biológicas, exames laboratoriais e seus resultados.

A estrutura será representada por modelos SQLAlchemy e criada no PostgreSQL exclusivamente por migrações Alembic. Assim, a definição do banco permanecerá versionada junto ao código da aplicação, sem depender da criação manual permanente de schemas ou tabelas.

O modelo foi elaborado para fins educacionais e servirá de base para as próximas etapas do projeto, especialmente a ingestão, a validação e o processamento de arquivos de dados.

## 2. Organização em schemas

O banco será dividido em schemas para separar responsabilidades e explicitar o estágio dos dados. Um schema é uma divisão lógica dentro do mesmo banco PostgreSQL, e não um banco independente.

### 2.1 Schema `ingestion`

O schema `ingestion` representa a camada de entrada e a origem dos dados. Neste MVP, ele armazenará o cadastro das fontes que fornecem registros à plataforma.

Em versões futuras, poderá receber estruturas relacionadas ao processo de ingestão, como arquivos, lotes e informações de rastreabilidade.

### 2.2 Schema `core`

O schema `core` representa os dados estruturados e confiáveis do domínio de saúde. Nele ficarão as entidades normalizadas usadas pela aplicação, com relacionamentos e regras de integridade protegidos pelo banco.

No modelo inicial, conterá pacientes pseudonimizados, tipos de exame, amostras biológicas, exames laboratoriais e resultados.

## 3. Entidades

### 3.1 Fonte de dados

A tabela `ingestion.data_sources` identifica a origem dos dados recebidos pela plataforma. Uma fonte poderá representar, por exemplo, um laboratório sintético, um arquivo ou outro sistema de origem.

| Campo | Tipo conceitual | Obrigatório | Regra |
| --- | --- | --- | --- |
| `id` | Inteiro | Sim | Chave primária |
| `name` | Texto | Sim | Valor único |
| `source_type` | Texto | Sim | Valor controlado |
| `description` | Texto | Não | Descrição livre da fonte |
| `is_active` | Booleano | Sim | Padrão verdadeiro |
| `created_at` | Data e hora | Sim | Gerado automaticamente |
| `updated_at` | Data e hora | Sim | Atualizado pela aplicação |

### 3.2 Paciente pseudonimizado

A tabela `core.patients` representa pacientes fictícios ou pseudonimizados. O modelo não armazenará nome, documento, endereço ou qualquer outro identificador pessoal direto.

| Campo | Tipo conceitual | Obrigatório | Regra |
| --- | --- | --- | --- |
| `id` | Inteiro | Sim | Chave primária |
| `external_code` | Texto | Sim | Código pseudonimizado e único |
| `birth_date` | Data | Não | Não identifica uma pessoa real |
| `biological_sex` | Texto | Não | Valor controlado |
| `created_at` | Data e hora | Sim | Gerado automaticamente |
| `updated_at` | Data e hora | Sim | Atualizado pela aplicação |

### 3.3 Tipo de exame

A tabela `core.exam_types` funciona como um catálogo padronizado dos exames reconhecidos pela plataforma. Ela separa a definição do exame de cada execução realizada para um paciente.

| Campo | Tipo conceitual | Obrigatório | Regra |
| --- | --- | --- | --- |
| `id` | Inteiro | Sim | Chave primária |
| `code` | Texto | Sim | Código único do tipo de exame |
| `name` | Texto | Sim | Nome do exame |
| `description` | Texto | Não | Descrição livre |
| `default_unit` | Texto | Não | Unidade de medida padrão |
| `value_type` | Texto | Sim | Tipo de resultado aceito, com valor controlado |
| `is_active` | Booleano | Sim | Padrão verdadeiro |

### 3.4 Amostra biológica

A tabela `core.biological_samples` representa o material biológico coletado de um paciente e utilizado na realização de exames, como sangue ou urina.

| Campo | Tipo conceitual | Obrigatório | Regra |
| --- | --- | --- | --- |
| `id` | Inteiro | Sim | Chave primária |
| `sample_code` | Texto | Sim | Código único da amostra |
| `patient_id` | Chave estrangeira | Sim | Referência a `core.patients.id` |
| `sample_type` | Texto | Sim | Tipo de material, com valor controlado |
| `collected_at` | Data e hora | Sim | Momento da coleta |
| `received_at` | Data e hora | Não | Momento do recebimento pelo laboratório |

### 3.5 Exame laboratorial

A tabela `core.laboratory_exams` representa uma execução concreta de exame para um paciente. Ela conecta o paciente, o tipo de exame, a fonte dos dados e, quando aplicável, a amostra biológica utilizada.

| Campo | Tipo conceitual | Obrigatório | Regra |
| --- | --- | --- | --- |
| `id` | Inteiro | Sim | Chave primária |
| `patient_id` | Chave estrangeira | Sim | Referência a `core.patients.id` |
| `exam_type_id` | Chave estrangeira | Sim | Referência a `core.exam_types.id` |
| `sample_id` | Chave estrangeira | Não | Referência a `core.biological_samples.id` |
| `data_source_id` | Chave estrangeira | Sim | Referência a `ingestion.data_sources.id` |
| `external_exam_code` | Texto | Sim | Código único do exame na origem |
| `status` | Texto | Sim | Situação do exame, com valor controlado |
| `requested_at` | Data e hora | Não | Momento da solicitação |
| `performed_at` | Data e hora | Não | Momento da realização |

### 3.6 Resultado de exame

A tabela `core.exam_results` armazena os componentes resultantes de um exame laboratorial. Um exame poderá possuir mais de um resultado, permitindo representar painéis compostos por diferentes medições.

| Campo | Tipo conceitual | Obrigatório | Regra |
| --- | --- | --- | --- |
| `id` | Inteiro | Sim | Chave primária |
| `laboratory_exam_id` | Chave estrangeira | Sim | Referência a `core.laboratory_exams.id` |
| `result_code` | Texto | Sim | Código do componente do resultado |
| `result_value_numeric` | Decimal | Condicional | Usado somente para resultado numérico |
| `result_value_text` | Texto | Condicional | Usado somente para resultado textual |
| `unit` | Texto | Não | Unidade de medida |
| `reference_range` | Texto | Não | Intervalo de referência informado pela origem |
| `is_abnormal` | Booleano | Não | Indica resultado fora da referência |

Cada resultado deverá possuir exatamente um valor: numérico ou textual. Os dois campos não poderão estar preenchidos simultaneamente nem permanecer ambos vazios.

## 4. Relacionamentos

Os relacionamentos entre as entidades são:

- uma fonte de dados pode estar associada a muitos exames laboratoriais;
- um paciente pode possuir muitas amostras biológicas;
- um paciente pode possuir muitos exames laboratoriais;
- um tipo de exame pode ser utilizado em muitos exames laboratoriais;
- uma amostra biológica pode estar associada a muitos exames laboratoriais, embora a associação seja opcional para o exame;
- um exame laboratorial pode possuir um ou muitos componentes de resultado.

O fluxo principal do domínio pode ser resumido da seguinte forma:

```text
Paciente ──< Amostra biológica
    │
    └──< Exame laboratorial >── Tipo de exame
                │
                ├── Fonte de dados
                │
                └──< Resultado de exame
```

As chaves estrangeiras garantirão que nenhum registro dependente seja associado a uma entidade inexistente.

## 5. Regras de integridade

O banco protegerá as seguintes regras:

- todas as tabelas possuirão uma chave primária inteira;
- o nome de uma fonte de dados será único;
- o código externo de um paciente será único;
- o código de um tipo de exame será único;
- o código de uma amostra biológica será único;
- o código externo de um exame laboratorial será único;
- campos essenciais serão obrigatórios;
- valores categóricos serão limitados aos conjuntos permitidos;
- amostras e exames somente poderão apontar para pacientes existentes;
- exames somente poderão apontar para tipos de exame e fontes existentes;
- uma amostra associada a um exame deverá existir;
- resultados somente poderão apontar para exames existentes;
- cada resultado terá valor numérico ou textual, mas nunca os dois ao mesmo tempo;
- o mesmo código de resultado não poderá ser repetido dentro de um exame;
- datas de recebimento e realização não poderão anteceder os eventos que logicamente as precedem, quando ambos os valores estiverem disponíveis.

Essas regras serão implementadas com chaves primárias, chaves estrangeiras, restrições de unicidade, campos não nulos e restrições de verificação (`CHECK`).

## 6. Decisões arquiteturais

- **Separação por schemas:** `ingestion` identifica a origem dos dados, enquanto `core` concentra os dados tratados do domínio.
- **Modelagem normalizada:** pacientes, tipos de exame, amostras, exames e resultados permanecem em tabelas distintas para reduzir repetição e preservar relacionamentos explícitos.
- **Pacientes pseudonimizados:** o modelo utiliza apenas um código externo e não prevê identificadores pessoais diretos.
- **Catálogo de tipos de exame:** a definição de um exame é separada de sua execução, permitindo padronização e reutilização.
- **Resultados flexíveis:** valores numéricos e textuais são suportados em campos separados e protegidos por uma regra de exclusividade.
- **Amostra opcional no exame:** alguns exames poderão ser registrados sem associação a uma amostra específica.
- **Rastreabilidade da origem:** todo exame terá uma fonte de dados obrigatória.
- **Datas com fuso horário:** eventos que representam instantes serão armazenados com informação de fuso horário.
- **Integridade no banco:** regras essenciais serão protegidas por constraints, sem depender exclusivamente da aplicação.
- **Estrutura versionada:** schemas, tabelas, índices e constraints serão criados e evoluídos por migrações Alembic.
- **Nomes previsíveis para constraints:** os modelos utilizarão uma convenção de nomes para facilitar migrações, mensagens de erro e manutenção.
- **Auditoria básica:** entidades que precisam de acompanhamento terão datas de criação e atualização. Neste MVP, `updated_at` será atualizado automaticamente quando a alteração ocorrer pelo ORM.

## 7. Limitações do modelo inicial

Este primeiro modelo possui limitações intencionais:

- não armazena dados identificáveis de pacientes reais;
- não implementa autenticação, autorização ou controle de acesso;
- não mantém histórico completo de alterações nos registros;
- não registra ainda arquivos, lotes ou execuções do processo de ingestão;
- não possui camada de staging para dados que aguardam validação;
- não modela instituições, profissionais de saúde, diagnósticos, medicamentos ou atendimentos;
- não utiliza terminologias clínicas padronizadas, como LOINC ou SNOMED CT;
- não converte automaticamente unidades de medida;
- não representa intervalos de referência de maneira estruturada;
- não inclui regras clínicas para interpretar resultados;
- a atualização automática de `updated_at` depende de operações feitas pelo ORM; atualizações SQL diretas deverão preencher o campo explicitamente;
- exclusões, retenção e anonimização de dados ainda não possuem políticas próprias.

## 8. Evoluções futuras

As próximas versões poderão ampliar o modelo com:

- controle de arquivos e lotes de ingestão;
- registro de linhas aceitas, rejeitadas e seus motivos;
- schemas adicionais, como `staging`, `quality` e `analytics`;
- rastreabilidade entre o registro de origem e o dado consolidado;
- deduplicação e reconciliação de pacientes e exames;
- histórico de alterações e auditoria detalhada;
- terminologias e códigos clínicos padronizados;
- unidades de medida estruturadas e conversões automáticas;
- intervalos de referência separados por contexto clínico;
- políticas de segurança, retenção e governança de dados;
- modelos analíticos e indicadores derivados dos dados consolidados.

O MVP 0.3.0 utilizará esta estrutura para ler um arquivo CSV, validar suas colunas e inserir os registros no banco sem criar tabelas manualmente.
