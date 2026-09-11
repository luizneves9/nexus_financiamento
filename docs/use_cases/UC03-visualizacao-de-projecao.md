# UC03 - Visualização de Projeção Financeira

**Status:** Parcialmente implementado  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF07, RN02

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc03---visualização-de-projeção)

## Objetivo

Permitir a consulta das parcelas projetadas de um contrato.

## Pre-condicoes

1. O contrato está cadastrado.
2. O contrato está selecionado na tela de contratos.
3. As estruturas de cálculo do banco estão disponíveis.

## Pos-condicoes

O usuário visualiza parcela, data de vencimento e valor calculado para o contrato selecionado.

## Fluxo principal

1. O usuário acessa a página de contratos.
2. O usuário seleciona exatamente um contrato.
3. O usuário aciona **Projeção**.
4. A aplicação consulta as matérialized views de projeção.
5. O sistema apresenta os valores em uma janela de diálogo.

## Fluxos alternativos

### FA01 - Contrato TFC

A consulta utiliza a matérialized view correspondente ao tipo de contrato. A
consulta atual combina os resultados retornados pelas views de projeção.

### FA02 - Exportação da projeção (fora do escopo atual)

A exportação não faz parte deste caso de uso no escopo atual. O download será
disponibilizado posteriormente em uma tela consolidada de projeções, com
filtros por contrato.

## Fluxos de exceção

### FE01 - Nenhum ou vários contratos selecionados

O sistema informa que exatamente um registro deve ser selecionado.

### FE02 - Projeção indisponível

O sistema informa a falha de consulta. Quando a consulta é executada sem
retornar parcelas, o sistema informa que a projeção não foi encontrada para o
contrato selecionado.

## Regras de negócio

- O cálculo e executado exclusivamente no PostgreSQL.
- Dias úteis consideram fins de semana e a tabela `financiamento.feriados`.
- A Selic e obtida conforme os triggers e views definidos no banco.
- Antecipacoes podem alterar a projeção quando registradas no banco.
