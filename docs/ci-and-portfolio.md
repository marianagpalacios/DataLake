# Integração contínua e preparação do portfólio

## 1. Objetivo

O MVP 0.8.0 automatiza as verificações de qualidade do DataLake e
consolida sua documentação para apresentação técnica.

## 2. Integração contínua

O workflow será executado em:

- Pull Requests direcionadas à `main`;
- pushes realizados na `main`;
- execuções manuais.

## 3. Jobs

### Quality

- instala o projeto;
- verifica a formatação;
- executa o linter;
- compila o código;
- constrói o pacote Python;
- valida os metadados da versão.

### Tests and coverage

- inicia PostgreSQL 17;
- utiliza banco exclusivo de testes;
- executa testes unitários, de integração, API e migrações;
- mede cobertura de linhas e branches;
- gera relatórios JUnit, XML e HTML.

### Docker build

- valida o Docker Compose;
- constrói a imagem da API;
- verifica se o pacote pode ser importado dentro da imagem.

## 4. Política de qualidade

Uma Pull Request não deve ser integrada quando:

- a formatação está incorreta;
- o Ruff encontra erros;
- a compilação falha;
- algum teste falha;
- a cobertura fica abaixo do limite;
- a imagem Docker não pode ser construída.

## 5. Segurança

O workflow utiliza apenas credenciais sintéticas para o banco de testes.

Nenhum segredo real é necessário para executar o CI.

## 6. Dependências

O Dependabot verificará:

- dependências Python;
- GitHub Actions;
- imagem Docker.

## 7. Documentação final

O projeto possuirá:

- README consolidado;
- arquitetura;
- guia de demonstração;
- changelog;
- guia de contribuição;
- política de segurança;
- templates de issues e Pull Requests.

## 8. Portfólio

O repositório deverá permitir que uma pessoa:

1. entenda o problema;
2. compreenda a arquitetura;
3. execute a plataforma;
4. reproduza o pipeline;
5. consulte a API;
6. execute os testes;
7. visualize a automação;
8. analise as decisões técnicas.