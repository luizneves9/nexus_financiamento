# UC04 - Exclusão Física de Contrato

**Status:** Implementado, sujeito a dependências de integridade  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF05, RN07, RN08, RN21

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc04---exclusão-física-de-contrato)

## Objetivo

Remover físicamente um contrato da tabela de contratos mediante confirmação do usuário.

## Pre-condicoes

1. O contrato está listado.
2. O usuário selecionou exatamente um contrato.
3. O usuário confirmou a exclusão.
4. O contrato não possui registros dependentes que bloqueiem a operação, ou
	esses registros foram tratados conforme o procedimento operacional vigente.

## Pos-condicoes

O registro do contrato é removido de `financiamento.contratos` quando a transação é concluída; a projeção dele (`projecao_parcelas`, `projecao_controle`) e os vínculos ERP são removidos junto (ON DELETE CASCADE).

## Fluxo principal

1. O usuário seleciona um contrato.
2. O usuário aciona **Excluir**.
3. O sistema apresenta os dados do contrato para conferencia.
4. O usuário seleciona **Confirmar**.
5. A aplicação executa `DELETE` no banco.
6. O sistema informa o sucesso e atualiza a listagem.

## Fluxos alternativos

### FA01 - Cancelar exclusão

O usuário seleciona **Cancelar**. Nenhum dado e alterado.

## Fluxos de exceção

### FE01 - Selecao invalida

O sistema exige exatamente um contrato selecionado.

### FE02 - Contrato com liquidação

Antes do `DELETE`, o sistema verifica se o contrato tem liquidação (ativa ou
estornada) e informa "Contrato possui parcelas liquidadas e não pode ser
excluído." (RN21). Essa verificação é uma validação e não grava log.

### FE03 - Integridade referencial

Quando o banco recusa a exclusão por vínculo (bens, antecipações, quitações ou
liquidações), o sistema informa "Contrato possui antecipações, quitações ou
liquidações vinculadas e não pode ser excluído."; a falha é registrada no log.

### FE04 - Falha de banco

A aplicação informa o erro e a transação não deve ser considerada concluida.

## Regras de negócio

- Nestá fase a exclusão e física.
- A exclusão lógica será avaliada posteriormente.
- Auditoria e registro do usuário que excluiu estão planejados para evolução
	futura.

## Auditoria

A exclusão registra `CONTRATO_EXCLUIR` em `financiamento.log_auditoria` na mesma transação do `DELETE`, com a cópia completa do contrato excluído em `detalhes` (`DELETE ... RETURNING *`). Exclusões bloqueadas pelo banco, como contrato com antecipação, são registradas com `sucesso = false` e o motivo, e a tela informa o motivo (RF08.1, RN12).
