# UC10 - Relatório de Endividamento

**Status:** Implementado  
**Ator principal:** Usuario responsável pelo setor financeiro  
**Requisitos associados:** RF07.4, RN02, RN03

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc10---relatório-de-endividamento)

## Objetivo

Exibir, em uma única tela, a projeção de pagamentos agrupada por ano e mês em 
um formato de tabela consolidada (fluxo de caixa), permitindo visualização 
dinâmica com suporte a tema claro/escuro.

## Pre-condicoes

1. A aplicação está disponível.
2. A conexão com o PostgreSQL está disponível.
3. A view `financiamento.vw_agrupamento_projecao` está disponível no banco.

## Pos-condicoes

O usuário visualiza o endividamento bancário agrupado por ano e mês em uma 
tabela com valores formatados em milhões (3 casas decimais), com suporte a 
alternância de tema.

## Fluxo principal

1. O usuário acessa o menu **Relatórios**.
2. O usuário abre a página **Endividamento**.
3. O sistema consulta a query que extrai ano, mês e total_parcela de 
   `vw_agrupamento_projecao`.
4. O sistema transforma os dados em estrutura de saldo acumulado e agrupamento 
   por ano/modalidade.
5. O sistema exibe a tabela HTML com formatação de tema automático (baseada no 
   SO/Streamlit do usuário).
6. O usuário pode alternar manualmente entre tema automático, claro ou escuro 
   usando os botões.

## Fluxos alternativos

### FA01 - Alternância manual de tema

O usuário pode clicar em um dos botões (🔄 Automático, ☀️ Claro, 🌙 Escuro) 
para forçar um tema específico. Ao retornar ao modo automático, a tabela volta 
a respeitar `@media (prefers-color-scheme)` do navegador/SO.

### FA02 - Nenhum registro encontrado

O sistema exibe um aviso "Nenhum dado disponível para o endividamento." quando 
a query retorna sem linhas.

## Fluxos de exceção

### FE01 - Falha na consulta

Quando a consulta ao banco falha, o sistema retorna um DataFrame vazio e 
exibe o aviso padrão sem dados.

## Regras de negócio

- O agrupamento e o cálculo são executados exclusivamente no PostgreSQL (RN02).
- Dias úteis, finais de semana e feriados cadastrados em `financiamento.feriados` 
  seguem RN03, refletidos no agrupamento exibido.
- Valores são formatados em milhões com 3 casas decimais (ex: 7.536).
- Separador decimal é ponto (.) e separador de milhar é vírgula (,) 
  (formato americano).
- A tabela respeita automaticamente o tema do SO/Streamlit quando em modo "auto".
- Nenhuma regra de negócio nova foi criada: o relatório expõe, de forma 
  consolidada, cálculos já governados por RN02 e RN03.

## Dados consultados

Os campos exibidos vêm da query que extrai:
- `ano` (EXTRACT YEAR de data_vcto)
- `mes` (EXTRACT MONTH de data_vcto)
- `categoria` (literal 'Financiamento')
- `valor` (SUM de total_parcela dividido por 1 milhão, arredondado para 3 decimais)

Estrutura final na tela:
- Saldo Acumulado (total geral)
- Blocos por ano (com linhas de modalidade, colunas de mês)

## Dados persistidos

Nenhum dado é persistido ou alterado por esta funcionalidade — é somente leitura.

## Interface

- Localização: **Relatórios > Endividamento**
- Componentes:
  - Título e descrição
  - 3 botões de alternância de tema (🔄 Automático, ☀️ Claro, 🌙 Escuro)
  - Tabela HTML com CSS responsivo (`@media prefers-color-scheme`)
  - Notificações de sucesso/erro (se aplicável)
