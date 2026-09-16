# UC09 - Relatório de Projeção de Pagamentos

**Status:** Implementado  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF07.3, RN02, RN03

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc09---relatório-de-projeção-de-pagamentos)

## Objetivo

Exibir, em uma única tela, o agrupamento da projeção de pagamentos de todos
os contratos, permitindo consulta consolidada sem a necessidade de
selecionar um contrato individualmente (como exige o UC03).

## Pre-condicoes

1. A aplicação está disponível.
2. A conexão com o PostgreSQL está disponível.
3. A view `financiamento.vw_agrupamento_projecao` está disponível no banco.

## Pos-condicoes

O usuário visualiza o agrupamento da projeção de pagamentos retornado pela
view `financiamento.vw_agrupamento_projecao`.

## Fluxo principal

1. O usuário acessa o menu **Relatórios**.
2. O usuário abre a página **Projeção de Pagamentos**.
3. O sistema consulta a view `financiamento.vw_agrupamento_projecao`.
4. O sistema exibe o resultado em uma tabela.

## Fluxos alternativos

### FA01 - Nenhum registro encontrado

O sistema exibe uma tabela sem registros. O usuário pode retornar a consulta
posteriormente.

### FA02 - Filtros e exportação (fora do escopo atual)

Filtros por contrato, período ou banco e a exportação/download do relatório
fazem parte da evolução planejada da "tela consolidada de projeções"
prevista no roadmap.

## Fluxos de exceção

### FE01 - Falha na consulta

Quando a consulta falha, o sistema apresenta a tabela vazia, sem mensagem
explícita de indisponibilidade (mesma limitação registrada no UC02).

## Regras de negócio

- O agrupamento e o cálculo continuam sendo executados exclusivamente no
  PostgreSQL (RN02), herdando o mesmo motor de projeção usado no UC03.
- Dias úteis, finais de semana e feriados cadastrados em
  `financiamento.feriados` seguem RN03, refletidos no agrupamento exibido.
- A tela não permite seleção de linhas nem ações sobre os registros; é uma
  consulta somente leitura, sem botões.
- Nenhuma regra de negócio nova foi criada para esta funcionalidade: o
  relatório apenas expõe, de forma consolidada, cálculos já governados por
  RN02 e RN03.

## Dados consultados

Os campos exibidos são definidos por `financiamento.vw_agrupamento_projecao`.
Esta view ainda não está documentada no DDL versionado
(`database/ddl_financiamento.sql`) — ver pendência em
[database/README.md](../../database/README.md).
