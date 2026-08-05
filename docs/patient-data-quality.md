# Qualidade de dados na ingestão de pacientes

## 1. Objetivo

Este documento descreve as regras de qualidade aplicadas aos pacientes
recebidos por CSV no MVP 0.4.0.

O fluxo separa registros válidos e inválidos, permite que dados válidos
continuem e gera um relatório local com os registros rejeitados e seus
respectivos motivos.

## 2. Tipos de erro

### 2.1 Erros estruturais

Erros estruturais afetam o arquivo inteiro e interrompem a ingestão:

- arquivo inexistente;
- arquivo vazio;
- CSV malformado;
- colunas obrigatórias ausentes;
- arquivo sem registros.

### 2.2 Erros de conteúdo

Erros de conteúdo afetam somente determinadas linhas:

- código externo vazio;
- código externo duplicado no arquivo;
- data com formato inválido;
- data de nascimento futura;
- sexo biológico inválido.

Registros com esses erros são rejeitados individualmente.

## 3. Códigos de qualidade

| Código | Campo | Significado |
|---|---|---|
| `required_value_missing` | `external_code` | Valor obrigatório ausente |
| `duplicate_in_file` | `external_code` | Código repetido no mesmo arquivo |
| `invalid_date_format` | `birth_date` | Data fora de `AAAA-MM-DD` |
| `future_birth_date` | `birth_date` | Data posterior ao dia da execução |
| `invalid_biological_sex` | `biological_sex` | Valor fora da lista permitida |

## 4. Registros duplicados no arquivo

Quando um código aparece mais de uma vez, todas as ocorrências são
rejeitadas.

O sistema não escolhe arbitrariamente qual linha deve ser considerada
correta.

## 5. Arquivo de rejeições

Quando existirem registros inválidos, será criado um arquivo em:

`data/rejected`

O arquivo conterá:

- dados originais;
- número da linha no CSV;
- códigos dos erros;
- campos com problemas;
- mensagens explicativas.

## 6. Métricas

A ingestão apresentará:

- registros recebidos;
- registros válidos;
- registros rejeitados;
- registros inseridos;
- registros já existentes;
- taxa de aceitação;
- avisos de normalização.

## 7. Taxa de aceitação

A taxa de aceitação será calculada por:

`registros válidos / registros recebidos × 100`

Pacientes válidos que já existam no banco continuam sendo considerados
válidos, embora não sejam inseridos novamente.

## 8. Status

A execução poderá terminar como:

- `completed`: nenhum registro foi rejeitado;
- `completed_with_rejections`: o processo terminou, mas houve rejeições;
- erro fatal: o arquivo não pôde ser processado.

## 9. Segurança

Os arquivos da pasta `data/rejected` não devem ser versionados.

Mesmo quando utilizados dados sintéticos, o projeto mantém essa proteção
para representar o comportamento esperado em dados sensíveis.

## 10. Limitações

Nesta versão:

- os relatórios são arquivos locais;
- não existe histórico de execuções no banco;
- não existe staging;
- não existe hash do arquivo;
- não existe correção automática;
- somente pacientes em CSV são processados.