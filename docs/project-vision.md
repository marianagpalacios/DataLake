# Visão do Projeto DataLake

## 1. Contexto

Laboratórios, clínicas, hospitais, instituições de pesquisa e sistemas de informação em saúde produzem grandes volumes de dados diariamente. Esses dados podem representar pacientes, amostras biológicas, exames laboratoriais, resultados clínicos, unidades de medida, instituições de origem e informações sobre coletas e processamentos.

Entretanto, essas informações nem sempre são produzidas de maneira padronizada. Sistemas diferentes podem representar o mesmo dado utilizando nomes de campos, códigos, formatos e estruturas distintas.

Um laboratório pode, por exemplo, enviar um arquivo com as seguintes colunas:

patient_id, exam_name, result, unit, collected_at

Enquanto outro laboratório pode representar as mesmas informações desta forma:

paciente, codigo_exame, valor_resultado, unidade_medida, data_coleta

Além das diferenças nos nomes das colunas, também podem existir variações em:

- formatos de datas;
- separadores decimais;
- códigos de exames;
- unidades de medida;
- identificação de pacientes;
- preenchimento de valores ausentes;
- organização dos arquivos;
- tipos de dados;
- regras utilizadas por cada sistema de origem.

Em projetos de saúde, pesquisa e bioinformática, essas diferenças dificultam a integração e a análise conjunta dos dados. Antes que as informações possam ser utilizadas com segurança, elas precisam ser recebidas, validadas, padronizadas, armazenadas e disponibilizadas de maneira rastreável.

O projeto DataLake será desenvolvido como uma plataforma educacional de engenharia de dados em saúde. Seu propósito é simular, em menor escala, desafios encontrados em projetos reais de integração de dados, como plataformas de pesquisa, Data Lakes institucionais e iniciativas semelhantes ao Projeto SABIÁ da UTFPR.

Para preservar a segurança e a privacidade, o projeto utilizará somente dados sintéticos, fictícios, públicos ou adequadamente anonimizados.

## 2. Problema

A integração de dados de saúde provenientes de diferentes sistemas apresenta desafios técnicos e organizacionais.

Quando cada fonte utiliza estruturas e padrões próprios, torna-se difícil consolidar os dados em uma base única e confiável. Um mesmo exame pode possuir nomes, códigos ou unidades diferentes dependendo do sistema de origem. Datas podem estar em formatos incompatíveis, valores numéricos podem utilizar separadores diferentes e determinados registros podem apresentar informações obrigatórias ausentes.

Sem um processo estruturado de ingestão e validação, podem ocorrer problemas como:

- registros duplicados;
- dados incompletos;
- valores inválidos;
- inconsistências entre fontes;
- perda da origem do dado;
- dificuldade para identificar quando um arquivo foi processado;
- dificuldade para descobrir quais transformações foram aplicadas;
- impossibilidade de reproduzir uma carga anterior;
- armazenamento de informações incorretas;
- falhas silenciosas durante o processamento.

Também pode ser difícil responder perguntas importantes, como:

- De qual arquivo este registro veio?
- Qual sistema produziu esse dado?
- Quando a informação foi importada?
- Quais registros foram rejeitados?
- Por que determinado registro foi considerado inválido?
- O arquivo já havia sido processado anteriormente?
- Quais transformações foram aplicadas aos dados?
- Quantos registros foram recebidos, aceitos e rejeitados?

Em dados relacionados à saúde, esses problemas são especialmente relevantes, pois informações incorretas ou sem rastreabilidade podem comprometer análises, pesquisas e tomadas de decisão.

Portanto, o problema central do projeto é a ausência de um fluxo padronizado, seguro e rastreável para receber, validar, transformar, armazenar e disponibilizar dados de saúde provenientes de diferentes fontes.

## 3. Objetivo

O objetivo do projeto DataLake é desenvolver uma plataforma educacional de engenharia de dados em saúde capaz de simular o recebimento, processamento, armazenamento e disponibilização de dados provenientes de diferentes fontes.

A plataforma deverá permitir que arquivos e outras fontes de dados sejam processados de maneira controlada, registrando informações sobre cada ingestão e aplicando regras de validação antes que os dados sejam considerados confiáveis.

O sistema deverá ser capaz de:

- receber dados em diferentes formatos;
- preservar os dados originais recebidos;
- registrar a origem de cada carga;
- identificar quando e como os dados foram processados;
- validar estruturas, campos e tipos de dados;
- padronizar nomes, formatos e valores;
- identificar registros inválidos ou duplicados;
- separar dados aceitos de dados rejeitados;
- armazenar dados estruturados em PostgreSQL;
- manter rastreabilidade entre os dados armazenados e suas fontes;
- disponibilizar informações para consultas e análises;
- gerar indicadores sobre a qualidade das cargas;
- permitir a evolução controlada da estrutura do banco de dados;
- disponibilizar futuramente uma API REST para consulta.

O projeto também possui um objetivo educacional. Durante seu desenvolvimento, serão aplicados conceitos de:

- modelagem de banco de dados;
- SQL;
- pipelines ETL;
- ingestão de dados;
- qualidade de dados;
- arquitetura de software;
- APIs REST;
- testes automatizados;
- versionamento;
- conteinerização;
- documentação;
- integração contínua.

Ao final, o projeto deverá demonstrar não apenas conhecimento em ferramentas específicas, mas também capacidade de organizar e evoluir uma solução de software de forma profissional.

## 4. Usuários

Os possíveis usuários ou beneficiários da plataforma incluem:

### Desenvolvedores de software

Poderão utilizar a plataforma para consultar dados, integrar novas funcionalidades, manter a API e evoluir os componentes da aplicação.

### Engenheiros de dados

Poderão criar, executar e manter pipelines de ingestão, transformação e validação de dados.

### Analistas de dados

Poderão consultar informações estruturadas e confiáveis para gerar relatórios, indicadores e análises.

### Cientistas de dados

Poderão utilizar os dados tratados como entrada para análises estatísticas, modelos preditivos e experimentos de aprendizado de máquina.

### Pesquisadores

Poderão acessar conjuntos de dados organizados e rastreáveis para apoiar estudos científicos.

### Profissionais de bioinformática

Poderão utilizar conceitos semelhantes para organizar metadados de amostras, resultados laboratoriais, informações genômicas e saídas de pipelines computacionais.

### Equipes de qualidade de dados

Poderão acompanhar registros rejeitados, inconsistências, duplicidades e indicadores de qualidade das cargas.

### Administradores da plataforma

Poderão acompanhar o funcionamento dos serviços, as execuções dos pipelines e os erros registrados.

### Professores, avaliadores e recrutadores

Poderão analisar o projeto como demonstração prática de conhecimentos em Engenharia de Software, banco de dados e Engenharia de Dados.

### Estudantes e novos bolsistas

Poderão utilizar a documentação para compreender a arquitetura, configurar o ambiente e contribuir com a evolução do projeto.

## 5. Fontes de dados

A plataforma poderá receber dados provenientes de diferentes fontes, simulando cenários encontrados em sistemas reais de saúde e pesquisa.

### Arquivos CSV

Os arquivos CSV serão utilizados inicialmente por serem comuns em exportações de sistemas laboratoriais, planilhas e bancos de dados.

Exemplos:

- cadastro de pacientes fictícios;
- informações de amostras;
- catálogo de exames;
- resultados laboratoriais;
- registros de coletas.

### Arquivos JSON

Arquivos JSON poderão representar dados estruturados ou semiestruturados, especialmente informações recebidas de APIs ou sistemas web.

Exemplos:

- eventos de processamento;
- resultados de serviços externos;
- metadados de exames;
- respostas de APIs.
### APIs REST

Futuramente, a plataforma poderá consumir dados disponibilizados por APIs externas.

Exemplos:

- sistemas laboratoriais;
- sistemas hospitalares;
- catálogos públicos;
- serviços de terminologia;
- plataformas de pesquisa.
### Bancos de dados relacionais

A plataforma poderá simular a extração de dados de outros bancos de dados, utilizando consultas SQL ou conexões controladas.

### Arquivos de planilha

Arquivos em formato de planilha poderão ser utilizados como fonte de dados, especialmente em cenários nos quais equipes realizam controles manuais.

### Arquivos de texto

Arquivos de texto poderão conter registros simples, logs ou informações geradas por outros sistemas.

### Dados sintéticos

O projeto utilizará dados sintéticos gerados especificamente para testes e demonstrações.

Esses dados deverão:

- representar situações realistas;
- incluir casos válidos;
- incluir casos inválidos;
- incluir registros duplicados;
- incluir valores ausentes;
- não identificar pessoas reais;
- poder ser compartilhados com segurança no GitHub.

### Dados públicos

Também poderão ser utilizados conjuntos de dados públicos, desde que suas condições de uso permitam o armazenamento e o processamento no projeto.

### Fontes futuras relacionadas à bioinformática

Em etapas futuras, poderão ser simulados metadados de arquivos como:

- FASTA;
- FASTQ;
- VCF;
- resultados de sequenciamento;
- metadados de amostras biológicas;
- informações de pipelines genômicos.

Inicialmente, o foco não será processar diretamente arquivos genômicos de grande volume, mas organizar seus metadados e simular a rastreabilidade de seu processamento.

## 6. Funcionalidades previstas

As funcionalidades serão desenvolvidas de forma progressiva durante os diferentes MVPs do projeto.

---

### Infraestrutura e configuração

- Execução do PostgreSQL com Docker;
- Configuração dos serviços com Docker Compose;
- Uso de variáveis de ambiente;
- Persistência dos dados em volumes;
- Verificação automática da disponibilidade do banco;
- Configuração reproduzível do ambiente de desenvolvimento.

---

### Organização do projeto

- Estrutura modular do código;
- Separação de responsabilidades;
- Configuração centralizada;
- Gerenciamento de dependências;
- Documentação da arquitetura;
- Convenções de código e versionamento.

---

### Modelagem de dados

- Criação do modelo conceitual;
- Criação do modelo lógico;
- Criação do modelo físico;
- Definição de entidades e relacionamentos;
- Criação de chaves primárias e estrangeiras;
- Criação de restrições de integridade;
- Criação de índices;
- Uso de schemas do PostgreSQL.

---

### Versionamento do banco de dados

- Criação de migrações;
- Aplicação automática das alterações;
- Reversão controlada de migrações;
- Histórico da evolução da estrutura do banco;
- Utilização do Alembic.

---

### Ingestão de dados

- Leitura de arquivos CSV;
- Leitura de arquivos JSON;
- Registro das cargas realizadas;
- Identificação da fonte dos dados;
- Armazenamento do nome e do caminho do arquivo;
- Armazenamento da data e da hora de processamento;
- Geração de identificador para cada execução;
- Detecção de arquivos processados anteriormente.

---

### Camada de dados brutos

- Preservação dos arquivos originais;
- Separação entre dados brutos e dados processados;
- Registro de metadados dos arquivos recebidos;
- Armazenamento do hash dos arquivos para identificação.

---

### Camada de staging

- Armazenamento temporário dos dados recebidos;
- Preparação dos registros antes da carga definitiva;
- Validação inicial dos campos;
- Apoio à investigação de erros.

---

### Transformação de dados

- Renomeação de colunas;
- Conversão de tipos;
- Padronização de datas;
- Padronização de valores textuais;
- Tratamento de valores ausentes;
- Padronização de unidades;
- Normalização de códigos;
- Preparação dos dados para o modelo principal.

---

### Qualidade de dados

- Validação de campos obrigatórios;
- Validação de formatos;
- Validação de tipos de dados;
- Identificação de valores impossíveis;
- Identificação de duplicidades;
- Validação de relacionamentos;
- Registro de problemas encontrados;
- Classificação dos erros;
- Cálculo de indicadores de qualidade;
- Geração de resumo de cada carga.

---

### Tratamento de registros rejeitados

- Armazenamento dos registros inválidos;
- Registro do motivo da rejeição;
- Associação do registro rejeitado à carga de origem;
- Possibilidade de análise posterior;
- Separação entre erros estruturais e erros de conteúdo.

---

### Rastreabilidade

- Registro da origem de cada dado;
- Associação entre arquivos e cargas;
- Associação entre registros processados e arquivos;
- Registro das transformações aplicadas;
- Histórico das execuções;
- Acompanhamento do status dos pipelines.

---

### Idempotência

- Prevenção de duplicidades durante reprocessamentos;
- Identificação de arquivos já processados;
- Possibilidade de executar novamente um pipeline de forma controlada;
- Manutenção da consistência do banco.

---

### Consultas SQL

- Consultas sobre pacientes fictícios;
- Consultas sobre exames;
- Consultas sobre resultados;
- Consultas sobre cargas;
- Consultas sobre registros rejeitados;
- Geração de indicadores;
- Criação de views.

---

### API REST

- Endpoint de verificação de funcionamento;
- Consulta de cargas;
- Consulta de detalhes de uma ingestão;
- Consulta de exames;
- Consulta de resultados;
- Consulta de problemas de qualidade;
- Paginação;
- Filtros;
- Documentação automática da API.

---

### Logs e observabilidade

- Registro do início e do fim das execuções;
- Registro de erros;
- Registro de alertas;
- Identificação do componente que gerou o log;
- Uso de logs estruturados;
- Acompanhamento do status dos serviços.

---

### Testes

- Testes unitários;
- Testes de transformação;
- Testes de validação;
- Testes de integração com o banco;
- Testes dos repositórios;
- Testes da API;
- Testes de comportamento dos pipelines;
- Banco exclusivo para testes.

---

### Integração contínua

- Execução automática dos testes;
- Análise de qualidade do código;
- Validação da formatação;
- Verificação de falhas antes do merge;
- Configuração com GitHub Actions.

---

### Documentação

- README com instruções de execução;
- Documentação da arquitetura;
- Documentação do banco;
- Diagramas;
- Exemplos de dados;
- Decisões arquiteturais;
- Instruções para contribuição;
- Histórico das versões.

## 7. Escopo do MVP 0.1.0

O **MVP 0.1.0** será dedicado à criação da base estrutural e da infraestrutura inicial do projeto.

Neste primeiro MVP serão entregues:

- Repositório organizado no GitHub;
- Branch específica para desenvolvimento do MVP;
- Estrutura inicial de diretórios;
- Projeto Python configurado;
- Arquivo `pyproject.toml`;
- Pacote Python localizado em `src/datalake`;
- Ambiente virtual local;
- Possibilidade de instalar o projeto em modo editável;
- Arquivo `.gitignore`;
- Arquivo `.editorconfig`;
- Arquivo `.env.example`;
- Proteção do arquivo `.env`;
- Configuração do PostgreSQL com Docker Compose;
- Definição explícita da versão da imagem do PostgreSQL;
- Criação de volume persistente;
- Configuração de *health check* do banco;
- Documentação da visão do projeto;
- Documentação das instruções de execução;
- Validação da conexão com o PostgreSQL;
- Histórico de commits organizado;
- Pull Request referente ao MVP;
- Tag de versão **v0.1.0**;
- Release correspondente no GitHub.

---

### Arquitetura do MVP

```text
Projeto Python
      │
      ▼
Docker Compose
      │
      ▼
PostgreSQL
      │
      ▼
Volume Persistente
```

---

### Objetivo do MVP

O principal objetivo desta versão é garantir que qualquer desenvolvedor autorizado consiga:

- Clonar o repositório;
- Configurar as variáveis locais;
- Iniciar o banco de dados;
- Compreender a estrutura inicial do projeto.

---

## 8. Fora do escopo do MVP 0.1.0

As seguintes funcionalidades **não serão implementadas** nesta primeira versão:

#### Banco de dados

- Modelagem completa das entidades de saúde;
- Criação das tabelas do domínio;
- Cadastro de pacientes;
- Cadastro de exames;
- Armazenamento de resultados laboratoriais.

### ETL e processamento

- Criação de pipelines ETL;
- Ingestão de arquivos CSV;
- Ingestão de arquivos JSON;
- Transformação de dados;
- Uso do Pandas;
- Uso do SQLAlchemy;
- Criação de migrações com Alembic;
- Regras de qualidade dos dados;
- Detecção de duplicidades;
- Armazenamento de registros rejeitados;
- Rastreabilidade completa das cargas.

### API

- Criação de API REST;
- Uso do FastAPI;
- Autenticação;
- Autorização.

### Interface

- Interface gráfica.

### Testes

- Testes de integração;
- Testes da API;
- Cobertura de testes.

### DevOps

- GitHub Actions;
- Monitoramento;
- Dashboards.

### Integrações

- Integração com serviços externos;
- Processamento de dados genômicos;
- Implantação em serviços de nuvem;
- Utilização de dados reais de pacientes.

---

Todas essas funcionalidades serão desenvolvidas de forma progressiva nos próximos MVPs.

> **Importante:** durante o MVP 0.1.0 **não serão criadas tabelas manualmente no banco de dados**. A criação e evolução da estrutura do banco ocorrerão posteriormente por meio de **migrações versionadas**, garantindo rastreabilidade e reprodutibilidade.

## 9. Requisitos não funcionais

Os requisitos não funcionais definem as características de qualidade, segurança, confiabilidade e manutenção que deverão orientar todo o desenvolvimento do projeto.

---

### Segurança

O projeto deverá atender aos seguintes requisitos de segurança:

- As credenciais não deverão ser armazenadas diretamente no código-fonte;
- O arquivo `.env` não deverá ser enviado ao GitHub;
- Deverá existir um arquivo `.env.example` sem valores sensíveis;
- Nenhum dado pessoal ou clínico real deverá ser armazenado no repositório;
- Tokens, senhas e chaves privadas não deverão ser incluídos em commits;
- Os dados utilizados deverão ser sintéticos, públicos ou adequadamente anonimizados;
- O acesso futuro à API deverá considerar mecanismos de autenticação e autorização;
- Logs não deverão expor informações sensíveis.

---

### Privacidade

O projeto deverá preservar a privacidade dos dados utilizados.

Para isso:

- Os dados de demonstração não deverão permitir a identificação de pessoas reais;
- Identificadores fictícios deverão ser utilizados no lugar de dados pessoais;
- Informações clínicas reais não deverão ser utilizadas sem autorização, controle e justificativa;
- O projeto deverá considerar os princípios de minimização de dados;
- Apenas as informações estritamente necessárias deverão ser armazenadas.

---

### Rastreabilidade

Toda informação processada deverá possuir rastreabilidade.

Assim:

- Cada carga deverá possuir um identificador único;
- A origem dos dados deverá ser registrada;
- A data e a hora de cada processamento deverão ser armazenadas;
- O status das execuções deverá ser registrado;
- Registros rejeitados deverão permanecer associados à carga de origem;
- Transformações relevantes deverão ser documentadas;
- Alterações na estrutura do banco deverão ser versionadas.

---

### Reprodutibilidade

O ambiente deverá ser facilmente reproduzido por qualquer desenvolvedor.

Para isso:

- O ambiente deverá ser executável por meio de instruções documentadas;
- O PostgreSQL deverá ser iniciado utilizando Docker Compose;
- As versões importantes das tecnologias deverão ser definidas explicitamente;
- Configurações de exemplo deverão ser fornecidas;
- Todas as dependências Python deverão ser declaradas;
- Outra pessoa deverá conseguir reproduzir o ambiente local sem modificações adicionais.

---

### Manutenibilidade

A arquitetura deverá facilitar futuras evoluções.

Portanto:

- O código deverá ser organizado por responsabilidades;
- Módulos não deverão acumular funções sem relação entre si;
- Nomes de arquivos, classes, funções e variáveis deverão ser claros;
- Regras de negócio deverão permanecer separadas do acesso ao banco de dados;
- Os componentes deverão possuir baixo acoplamento;
- A duplicação de código deverá ser evitada;
- Refatorações deverão ser realizadas sempre que responsabilidades se tornarem confusas.

---

### Testabilidade

As funcionalidades deverão ser desenvolvidas de forma que possam ser testadas facilmente.

Assim:

- Regras de transformação deverão ser implementadas de forma testável;
- Componentes externos deverão ser isolados sempre que possível;
- Testes não deverão depender de dados pessoais reais;
- Deverá existir um banco separado para testes de integração;
- Funções deverão possuir responsabilidades pequenas e bem definidas.

---

### Confiabilidade

O sistema deverá apresentar comportamento previsível mesmo diante de falhas.

Para isso:

- Falhas de processamento não deverão ser ignoradas silenciosamente;
- Erros deverão ser registrados em logs;
- Transações deverão ser utilizadas quando necessário;
- Uma falha não deverá deixar o banco em estado parcialmente inconsistente;
- Reprocessamentos não deverão gerar duplicidades indevidas;
- O sistema deverá diferenciar execuções concluídas, concluídas com alertas e falhas.

---

### Integridade dos dados

O banco deverá preservar a consistência dos dados armazenados.

Assim:

- Chaves primárias e estrangeiras deverão ser utilizadas;
- Campos obrigatórios deverão possuir restrições;
- Valores incompatíveis deverão ser rejeitados;
- Relacionamentos inválidos não deverão ser permitidos;
- Duplicidades deverão ser controladas;
- As regras de domínio deverão ser aplicadas de forma consistente.

---

### Desempenho

O projeto deverá apresentar desempenho adequado para seu propósito.

Portanto:

- Consultas deverão ser analisadas antes da criação indiscriminada de índices;
- Operações em lote deverão ser preferidas para grandes quantidades de dados;
- O sistema deverá evitar consultas repetitivas desnecessárias;
- O desempenho deverá ser medido antes da implementação de otimizações complexas;
- Os pipelines deverão registrar informações sobre quantidade de registros processados e duração das execuções.

---

### Escalabilidade

A arquitetura deverá permitir crescimento gradual do projeto.

Assim:

- A inclusão de novas fontes de dados deverá ocorrer sem necessidade de grandes modificações;
- Novas transformações deverão poder ser adicionadas sem reescrever todo o sistema;
- A aplicação deverá possibilitar a separação futura entre API, banco de dados e processos de ingestão;
- O armazenamento bruto poderá ser migrado futuramente para soluções de armazenamento de objetos, como MinIO ou Amazon S3.

---

### Documentação

Toda a documentação deverá permanecer atualizada durante a evolução do projeto.

O projeto deverá possuir:

- README atualizado;
- Justificativas para decisões arquiteturais relevantes;
- Documentação dos comandos necessários para execução;
- Explicação da estrutura dos dados;
- Registro das principais alterações de cada MVP;
- Explicações sobre o propósito das tecnologias utilizadas.

---

### Portabilidade

O ambiente deverá funcionar de forma semelhante em diferentes computadores.

Para isso:

- Diferenças entre sistemas operacionais deverão ser reduzidas utilizando Docker;
- Caminhos absolutos específicos de uma máquina deverão ser evitados;
- Configurações locais deverão permanecer externas ao código-fonte.

---

### Versionamento

O desenvolvimento deverá seguir boas práticas de controle de versão.

Assim:

- Todo o código deverá ser versionado com Git;
- O desenvolvimento deverá ocorrer em branches;
- Os commits deverão representar alterações pequenas e coerentes;
- As mudanças deverão ser integradas por meio de Pull Requests;
- Cada MVP concluído deverá possuir uma tag correspondente;
- As versões deverão seguir uma convenção previamente definida.

---

### Usabilidade para desenvolvedores

O projeto deverá ser simples de compreender e configurar.

Para isso:

- A configuração inicial deverá exigir poucos passos;
- Mensagens de erro deverão ser claras e compreensíveis;
- Os comandos mais utilizados deverão estar documentados;
- A estrutura de diretórios deverá ser previsível;
- Novos colaboradores deverão conseguir compreender o projeto sem depender exclusivamente de explicações orais.

## 10. Riscos

O desenvolvimento de uma plataforma de dados em saúde envolve riscos técnicos, organizacionais e relacionados à segurança da informação. Identificar esses riscos antecipadamente permite definir estratégias para reduzir seus impactos durante o desenvolvimento do projeto.

---

### Exposição de dados sensíveis

Dados de saúde podem conter informações pessoais e clínicas sensíveis.

#### Impacto

- Violação de privacidade;
- Exposição indevida de pacientes;
- Comprometimento ético e legal;
- Perda de confiança no projeto.

#### Mitigação

- Utilizar somente dados sintéticos, públicos ou adequadamente anonimizados;
- Impedir o versionamento de arquivos locais;
- Não registrar informações sensíveis em logs;
- Revisar os arquivos antes de cada commit;
- Utilizar `.gitignore`;
- Manter credenciais fora do código.

---

### Versionamento acidental de credenciais

O arquivo `.env`, senhas ou tokens podem ser enviados ao GitHub por engano.

#### Impacto

- Acesso não autorizado;
- Comprometimento do banco de dados;
- Necessidade de revogar credenciais;
- Exposição de serviços.

#### Mitigação

- Incluir o arquivo `.env` no `.gitignore`;
- Utilizar um arquivo `.env.example`;
- Executar `git status` antes dos commits;
- Revisar a área de *staging* utilizando `git diff --cached`;
- Utilizar ferramentas de detecção de segredos futuramente.

---

### Dados inválidos

Arquivos podem conter valores ausentes, formatos incorretos ou informações impossíveis.

#### Impacto

- Análises incorretas;
- Falhas durante os pipelines;
- Armazenamento de dados não confiáveis;
- Comprometimento das consultas.

#### Mitigação

- Aplicar validações estruturais;
- Validar tipos e formatos;
- Rejeitar registros inválidos;
- Registrar os motivos das rejeições;
- Criar testes para as regras de qualidade.

---

### Registros duplicados

Um mesmo arquivo ou registro pode ser processado mais de uma vez.

#### Impacto

- Contagens incorretas;
- Resultados duplicados;
- Crescimento desnecessário do banco de dados;
- Análises inconsistentes.

#### Mitigação

- Utilizar identificadores únicos;
- Calcular o hash dos arquivos;
- Criar *constraints* no banco de dados;
- Implementar processos idempotentes;
- Registrar arquivos já processados.

---

### Perda de rastreabilidade

Os registros podem ser armazenados sem informação sobre sua origem.

#### Impacto

- Dificuldade para investigar erros;
- Impossibilidade de reproduzir resultados;
- Perda de confiança nos dados;
- Dificuldade para corrigir cargas.

#### Mitigação

- Registrar cada ingestão;
- Associar os registros à carga de origem;
- Armazenar metadados dos arquivos;
- Manter histórico de processamento;
- Documentar as transformações realizadas.

---

### Falhas de ingestão

O processamento pode ser interrompido por arquivos corrompidos, indisponibilidade do banco de dados ou erros inesperados.

#### Impacto

- Carga incompleta;
- Banco em estado inconsistente;
- Necessidade de intervenção manual;
- Perda de dados processados.

#### Mitigação

- Utilizar transações;
- Registrar o status das execuções;
- Tratar exceções;
- Permitir reprocessamento controlado;
- Armazenar logs;
- Criar testes simulando falhas.

---

### Alterações manuais no banco de dados

A estrutura do banco pode ser modificada diretamente sem registro no projeto.

#### Impacto

- Ambientes diferentes;
- Perda de reprodutibilidade;
- Dificuldade para identificar alterações;
- Falhas ao executar o projeto em outra máquina.

#### Mitigação

- Utilizar Alembic;
- Versionar todas as migrações;
- Evitar alterações manuais na estrutura;
- Revisar mudanças antes da aplicação.

---

### Falta de padronização

O código pode crescer sem uma separação clara de responsabilidades.

#### Impacto

- Manutenção difícil;
- Aumento da quantidade de erros;
- Duplicação de código;
- Dificuldade para adicionar novas funcionalidades.

#### Mitigação

- Manter uma arquitetura modular;
- Criar funções pequenas e coesas;
- Revisar responsabilidades periodicamente;
- Realizar refatorações quando necessário;
- Documentar decisões arquiteturais.

---

### Excesso de complexidade

O projeto pode adotar muitas tecnologias antes de existir uma necessidade real.

#### Impacto

- Dificuldade de aprendizado;
- Aumento do tempo de desenvolvimento;
- Arquitetura difícil de compreender;
- Possível abandono do projeto.

#### Mitigação

- Desenvolver por meio de MVPs;
- Introduzir tecnologias progressivamente;
- Justificar a utilização de cada ferramenta;
- Priorizar soluções simples;
- Refatorar apenas quando necessário.

---

### Dependência excessiva de bibliotecas

O projeto pode depender de abstrações sem compreender os conceitos fundamentais.

#### Impacto

- Dificuldade para diagnosticar erros;
- Conhecimento superficial das tecnologias;
- Uso inadequado das ferramentas.

#### Mitigação

- Aprender SQL antes de depender totalmente de um ORM;
- Compreender os processos executados pelas bibliotecas;
- Utilizar abstrações somente quando agregarem valor;
- Documentar as decisões técnicas.

---

### Falta de testes

Alterações podem quebrar funcionalidades já existentes.

#### Impacto

- Regressões;
- Comportamento inesperado;
- Baixa confiança nas entregas;
- Dificuldade para realizar refatorações.

#### Mitigação

- Adicionar testes progressivamente;
- Testar regras de negócio;
- Executar testes automaticamente;
- Integrar os testes ao GitHub Actions.

---

### Documentação desatualizada

O código pode evoluir sem que as instruções sejam atualizadas.

#### Impacto

- Dificuldade para executar o projeto;
- Entrada mais lenta de novos colaboradores;
- Utilização de comandos incorretos;
- Perda de credibilidade do portfólio.

#### Mitigação

- Atualizar a documentação a cada MVP;
- Incluir documentação na definição de pronto;
- Revisar o README antes de cada release;
- Manter exemplos executáveis.

---

### Dependência do ambiente local

O projeto pode funcionar apenas na máquina da desenvolvedora.

#### Impacto

- Impossibilidade de avaliação por terceiros;
- Dificuldades de colaboração;
- Falhas em outros sistemas operacionais.

#### Mitigação

- Utilizar Docker;
- Declarar todas as dependências do projeto;
- Evitar caminhos específicos da máquina;
- Documentar a configuração do ambiente;
- Validar o projeto em um ambiente limpo.

## 11. Critérios de sucesso

O projeto será considerado bem-sucedido quando demonstrar, de forma prática e documentada, a capacidade de receber, validar, transformar, armazenar e disponibilizar dados de saúde de maneira segura, organizada e rastreável.

---

### Critérios de sucesso do projeto completo

Ao final do desenvolvimento, uma pessoa autorizada deverá ser capaz de:

- Clonar o repositório;
- Configurar o ambiente local;
- Iniciar os serviços da aplicação;
- Executar as migrações do banco de dados;
- Carregar um conjunto de dados sintéticos;
- Acompanhar o status da ingestão;
- Consultar os dados armazenados;
- Identificar registros rejeitados;
- Compreender a origem dos registros;
- Executar os testes automatizados;
- Acessar a documentação da API;
- Compreender a arquitetura do projeto por meio da documentação.

---

### Funcionalidades esperadas da plataforma

Ao término do projeto, a plataforma deverá ser capaz de:

- Receber pelo menos duas fontes de dados com estruturas diferentes;
- Padronizar os dados em um modelo comum;
- Validar campos obrigatórios;
- Identificar dados inválidos;
- Detectar ou impedir duplicidades;
- Armazenar registros rejeitados juntamente com seus respectivos motivos;
- Registrar o início e o término de cada carga;
- Registrar quantos registros foram recebidos, aceitos e rejeitados;
- Manter a associação entre registros e suas respectivas fontes de origem;
- Permitir consultas diretamente por SQL;
- Disponibilizar consultas por meio de uma API REST;
- Possuir testes automatizados;
- Executar verificações automáticas utilizando GitHub Actions;
- Utilizar migrações para controlar a evolução do banco de dados;
- Disponibilizar documentação suficiente para reproduzir completamente o ambiente.

---

### Critérios de qualidade

O projeto deverá apresentar os seguintes indicadores de qualidade:

- Código legível;
- Responsabilidades bem separadas;
- Nomes claros e padronizados;
- Configuração segura;
- Ausência de credenciais no repositório;
- Dados sintéticos adequados ao contexto do projeto;
- Commits organizados;
- Pull Requests documentadas;
- Tags correspondentes aos MVPs;
- README atualizado;
- Decisões arquiteturais devidamente justificadas;
- Testes das principais regras de negócio;
- Histórico de evolução compreensível.

---

### Critérios de sucesso do portfólio

O repositório deverá permitir que professores, avaliadores e recrutadores compreendam facilmente:

- Qual problema está sendo resolvido;
- Por que a arquitetura foi escolhida;
- Como os dados percorrem toda a plataforma;
- Como a qualidade dos dados é controlada;
- Como as cargas são rastreadas;
- Como o banco de dados evolui ao longo do tempo;
- Como os testes protegem o sistema;
- Como executar o projeto localmente;
- Quais melhorias ainda poderão ser implementadas futuramente.

---

### Conhecimentos demonstrados

A apresentação do projeto deverá evidenciar domínio dos seguintes assuntos:

#### Banco de dados

- PostgreSQL;
- SQL;
- Modelagem de banco de dados.

#### Engenharia de dados

- Pipelines ETL;
- Qualidade de dados;
- Transformação de dados.

#### Desenvolvimento

- Python;
- Pandas;
- SQLAlchemy;
- Alembic;
- FastAPI;
- Pytest.

#### Infraestrutura

- Docker;
- Git;
- GitHub;
- GitHub Actions.

#### Engenharia de Software

- Arquitetura de software;
- Segurança de dados;
- Privacidade em dados de saúde.

---

### Critérios de sucesso do MVP 0.1.0

O primeiro MVP será considerado concluído quando:

- O repositório estiver clonado e configurado localmente;
- Existir uma branch específica para o desenvolvimento;
- A estrutura inicial de diretórios estiver criada;
- O projeto Python puder ser instalado corretamente;
- O pacote `datalake` puder ser importado sem erros;
- O PostgreSQL iniciar utilizando Docker Compose;
- O banco apresentar o status **healthy**;
- For possível executar uma consulta SQL simples;
- Os dados permanecerem armazenados em um volume persistente;
- O arquivo `.env` não estiver versionado;
- O arquivo `.env.example` estiver disponível;
- O README explicar claramente como iniciar o ambiente;
- O documento de visão do projeto estiver preenchido;
- Os commits estiverem organizados;
- Uma Pull Request tiver sido criada e revisada;
- As alterações tiverem sido integradas à branch `main`;
- A tag `v0.1.0` tiver sido criada;
- A release correspondente ao primeiro MVP tiver sido publicada.

---

### Indicadores futuros

Durante a evolução do projeto poderão ser monitorados diversos indicadores de desempenho e qualidade, tais como:

- Quantidade total de arquivos processados;
- Quantidade de registros recebidos;
- Quantidade de registros aceitos;
- Quantidade de registros rejeitados;
- Taxa de aceitação;
- Taxa de rejeição;
- Quantidade de duplicidades detectadas;
- Duração média das cargas;
- Quantidade de falhas de processamento;
- Quantidade de testes implementados;
- Cobertura de testes;
- Tempo necessário para configurar o ambiente;
- Quantidade de fontes de dados integradas.

---

### Considerações finais

O projeto não será considerado bem-sucedido apenas por utilizar diversas tecnologias.

Seu sucesso será determinado pela capacidade de resolver o problema proposto utilizando uma arquitetura:

- Compreensível;
- Segura;
- Testável;
- Reproduzível;
- Adequadamente documentada;
- Fácil de manter e evoluir ao longo do tempo.
