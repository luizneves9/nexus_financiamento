# UC08 - Atualizacao da Selic

**Status:** Dados no banco; integracao por API planejada  
**Ator principal:** Processo de integracao ou usuario autorizado  
**Requisitos associados:** RF01, RN02

## Objetivo

Disponibilizar no banco os valores da Selic necessarios para os calculos financeiros.

## Pre-condicoes

1. A fonte oficial ou API esta disponivel quando a integracao for implementada.
2. O processo possui credenciais e permissao de escrita.
3. A tabela `financiamento.selic` esta disponivel.

## Pos-condicoes

- Os valores recebidos sao persistidos por data.
- Contratos e antecipacoes podem localizar a taxa aplicavel.
- As estruturas de projecao podem ser atualizadas conforme o processo definido.

## Fluxo planejado

1. O processo consulta a API oficial.
2. O sistema valida data e valor recebidos.
3. O sistema evita duplicidade ou define a politica de atualizacao da mesma data.
4. O sistema grava os valores em `financiamento.selic`.
5. O sistema atualiza as estruturas de calculo quando necessario.
6. O processo registra sucesso ou falha operacional.

## Comportamento atual

A aplicacao nao realiza a importacao por API. Ela consulta os dados ja armazenados no banco. Triggers localizam a taxa mais recente aplicavel ao contrato ou a antecipacao.

## Fluxos de excecao

### FE01 - API indisponivel

O processo registra a falha e preserva os dados existentes.

### FE02 - Valor invalido

O sistema rejeita registros sem data ou com valor fora do dominio definido.

### FE03 - Taxa ausente para uma data

A projecao devera seguir a politica definida para ausencia de taxa. Essa
politica sera formalizada durante a implementacao da integracao.

## Regras de negocio

- A Selic e um insumo do calculo financeiro.
- A taxa do contrato e preenchida considerando a data BNDES.
- A taxa da antecipacao e preenchida considerando a data de tesouraria.
