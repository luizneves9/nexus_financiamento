# UC11 - Consulta de Antecipações

**Status:** Implementado  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF07.5, RN08, RN10

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc11---consulta-de-antecipações)

## Objetivo

Exibir, em uma única tela, todas as antecipações e quitações registradas nos
contratos (UC06), com filtros e um resumo dos valores, sem a necessidade de
abrir contrato por contrato.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. A conexão com o PostgreSQL está disponível.

## Pos-condicoes

O usuário visualiza os lançamentos de `financiamento.antecipacao` que
atendem aos filtros aplicados, com o resumo correspondente. Nenhum dado é
alterado.

## Fluxo principal

1. O usuário acessa o menu **Operacional** e abre a página **Antecipação**.
2. O sistema consulta `financiamento.antecipacao`, unindo `contratos`,
   `empresas` e `bancos` para obter o número do contrato e as razões sociais.
3. O sistema exibe a tabela com as colunas `id`, `nome_empresa`, `banco`,
   `numero_contrato`, `data_pagamento` (DD/MM/AAAA), `valor_pago` (formato
   brasileiro) e `tipo_lancamento` (`ANTECIPACAO` ou `QUITACAO`), ordenada
   por `id`.
4. Abaixo da tabela, o sistema exibe o resumo: quantidade de empresas,
   bancos e contratos distintos e o total pago.

## Fluxos alternativos

### FA01 - Filtrar lançamentos

1. O usuário preenche um ou mais filtros: **Empresa**, **Banco**,
   **Contrato** (busca parcial, sem diferenciar maiúsculas/minúsculas),
   **Pagamento de** e **Pagamento até** (intervalo de `data_pagamento`;
   qualquer extremidade pode ficar vazia).
2. O usuário aciona **Filtrar**.
3. O sistema refaz a consulta aplicando os filtros no banco e atualiza a
   tabela e o resumo.
4. Os filtros permanecem aplicados ao trocar de aba e voltar (estado
   exclusivo da página, prefixo `fa_`), até o usuário alterá-los ou sair do
   sistema.

### FA02 - Nenhum lançamento encontrado

O sistema exibe o aviso "Nenhuma antecipação encontrada com os filtros
aplicados." e não exibe tabela nem resumo.

## Fluxos de exceção

### FE01 - Falha na consulta

Quando a consulta falha, o sistema se comporta como em FA02 (mesma
limitação registrada no UC02 e no UC09).

## Regras de negócio

- Cada lançamento pertence a um contrato, que pertence a uma empresa e a um
  banco (RN08).
- A quitação total aparece como lançamento com `tipo_lancamento = QUITACAO`
  (RN10).
- A tela é somente leitura: o registro de novas antecipações continua no
  botão **Liquidar** da Gestão de Contratos (UC06).
- Consultas não são registradas no log de auditoria (RN12).

## Dados consultados

`financiamento.antecipacao` (`id`, `data_pagamento`, `valor_pago`,
`tipo_lancamento`), `financiamento.contratos` (`numero_contrato`),
`financiamento.empresas.razao_social` (como `nome_empresa`) e
`financiamento.bancos.razao_social` (como `banco`).

## Evidência

- `src/views/include_antecipation.py` (tela, filtros e resumo).
- `src/services/include_antecipation.py` (`listar_antecipacoes`,
  `resumir_antecipacoes`).
- `src/queries/queries_antecipacao.py` (`SELECT_ANTECIPACOES`).
