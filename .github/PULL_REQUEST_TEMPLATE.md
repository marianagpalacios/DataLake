## Objetivo

Descreva o problema resolvido por esta Pull Request.

## Alterações

- 
- 
- 

## Como validar

```powershell
python -m ruff format --check src tests
python -m ruff check src tests
python -m pytest
python -m compileall src tests
```

## Impactos
- Banco de dados
- Migrações
- API
- Pipeline ETL
- Qualidade dos dados
- Docker
- Documentação
- Testes

## Segurança e privacidade
- Nenhuma credencial foi adicionada.
- Nenhum dado real de saúde foi adicionado.
- Arquivos .env não foram versionados.
- Campos internos não foram expostos pela API.

## Checklist
- A alteração foi desenvolvida em branch.
- Os testes passam localmente.
- O CI está verde.
- A documentação foi atualizada.
- O código foi revisado.