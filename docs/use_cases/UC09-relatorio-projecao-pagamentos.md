# UC09 - Relatório de Projeção de Pagamentos

**Status:** Implementado  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF07.3, RN02, RN03

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc09---relatório-de-projeção-de-pagamentos)

## Objetivo

Exibir, em uma única tela, o agrupamento da projeção de pagamentos de todos
os contratos, permitindo consulta consolidada sem a necessidade de
selecionar um contrato individualmente (como exige o UC03), com filtros e
resumo dos valores.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. A conexão com o PostgreSQL está disponível.
3. A view `financiamento.vw_agrupamento_projecao` está disponível no banco.

## Pos-condicoes

O usuário visualiza o agrupamento da projeção de pagamentos retornado pela
view `financiamento.vw_agrupamento_projecao`, restrito aos filtros
aplicados, com o resumo correspondente.

## Fluxo principal

1. O usuário acessa o menu **Relatórios**.
2. O usuário abre a página **Projeção de Pagamentos**.
3. O sistema consulta a view `financiamento.vw_agrupamento_projecao`.
4. O sistema exibe o resultado em uma tabela, com datas em DD/MM/AAAA e
   valores em formato brasileiro.
5. Abaixo da tabela, o sistema exibe o resumo em uma linha: quantidade de
   empresas, bancos e contratos distintos e o total das parcelas
   (`total_parcela`).

## Fluxos alternativos

### FA01 - Filtrar a projeção

1. O usuário preenche um ou mais filtros: **Empresa** (`nome_empresa`),
   **Banco** (`banco`), **Contrato** (`numero_contrato`) — busca parcial, sem
   diferenciar maiúsculas/minúsculas — e **Vcto de** / **Vcto até**
   (intervalo de `data_vcto`; qualquer extremidade pode ficar vazia).
2. O usuário aciona **Filtrar**.
3. O sistema refaz a consulta aplicando os filtros no banco e atualiza a
   tabela e o resumo.
4. Os filtros permanecem aplicados ao trocar de aba e voltar (estado
   exclusivo da página, prefixo `fp_`), até o usuário alterá-los ou sair do
   sistema.

### FA02 - Nenhum registro encontrado

O sistema exibe o aviso "Nenhuma projeção encontrada com os filtros
aplicados." e não exibe tabela nem resumo.

### FA03 - Exportação (fora do escopo atual)

A exportação/download do relatório faz parte da evolução planejada
(BL-010).

## Fluxos de exceção

### FE01 - Falha na consulta

Quando a consulta falha, o sistema se comporta como em FA02, sem mensagem
explícita de indisponibilidade (mesma limitação registrada no UC02).

## Regras de negócio

- O agrupamento e o cálculo continuam sendo executados exclusivamente no
  PostgreSQL (RN02), herdando o mesmo motor de projeção usado no UC03.
- Dias úteis, finais de semana e feriados cadastrados em
  `financiamento.feriados` seguem RN03, refletidos no agrupamento exibido.
- A tela não permite ações sobre os registros; é uma consulta somente
  leitura (a coluna de seleção não aciona nenhuma operação).
- Consultas não são registradas no log de auditoria (RN12).
- Nenhuma regra de negócio nova foi criada para esta funcionalidade: o
  relatório apenas expõe, de forma consolidada, cálculos já governados por
  RN02 e RN03.

## Dados consultados

Os campos exibidos são definidos por `financiamento.vw_agrupamento_projecao`.
Esta view ainda não está documentada no DDL versionado
(`database/ddl_financiamento.sql`) — ver pendência em
[database/README.md](../../database/README.md).
