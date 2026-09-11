# UC04 - Exclusão Física de Contrato

**Status:** Implementado, sujeito a dependências de integridade  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF05, RN04

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

O registro do contrato e removido de `financiamento.contratos` quando a transação e concluida.

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

### FE02 - Integridade referencial

O banco pode impedir a exclusão quando existirem bens ou antecipações vinculados ao contrato.

### FE03 - Falha de banco

A aplicação informa o erro e a transação não deve ser considerada concluida.

## Regras de negócio

- Nestá fase a exclusão e física.
- A exclusão lógica será avaliada posteriormente.
- Auditoria e registro do usuário que excluiu estão planejados para evolução
	futura.
