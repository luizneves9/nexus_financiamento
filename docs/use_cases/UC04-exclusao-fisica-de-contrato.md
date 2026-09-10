# UC04 - Exclusao Fisica de Contrato

**Status:** Implementado, sujeito a dependencias de integridade  
**Ator principal:** Usuario responsavel pelo setor financeiro  
**Requisitos associados:** RF05, RN04

## Objetivo

Remover fisicamente um contrato da tabela de contratos mediante confirmacao do usuario.

## Pre-condicoes

1. O contrato esta listado.
2. O usuario selecionou exatamente um contrato.
3. O usuario confirmou a exclusao.
4. O contrato nao possui registros dependentes que bloqueiem a operacao, ou
	esses registros foram tratados conforme o procedimento operacional vigente.

## Pos-condicoes

O registro do contrato e removido de `financiamento.contratos` quando a transacao e concluida.

## Fluxo principal

1. O usuario seleciona um contrato.
2. O usuario aciona **Excluir**.
3. O sistema apresenta os dados do contrato para conferencia.
4. O usuario seleciona **Confirmar**.
5. A aplicacao executa `DELETE` no banco.
6. O sistema informa o sucesso e atualiza a listagem.

## Fluxos alternativos

### FA01 - Cancelar exclusao

O usuario seleciona **Cancelar**. Nenhum dado e alterado.

## Fluxos de excecao

### FE01 - Selecao invalida

O sistema exige exatamente um contrato selecionado.

### FE02 - Integridade referencial

O banco pode impedir a exclusao quando existirem bens ou antecipacoes vinculados ao contrato.

### FE03 - Falha de banco

A aplicacao informa o erro e a transacao nao deve ser considerada concluida.

## Regras de negocio

- Nesta fase a exclusao e fisica.
- A exclusao logica sera avaliada posteriormente.
- Auditoria e registro do usuario que excluiu estao planejados para evolucao
	futura.
