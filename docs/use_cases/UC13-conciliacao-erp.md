# UC13 - Conciliação com o ERP

**Status:** Implementado
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.6, RF07.7, RF09, RN19, RN20, RN22, RN23, RN12

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc13---conciliação-com-o-erp)

## Objetivo

Liquidar as parcelas a partir do relatório de pagamentos do ERP (boletos e
débito em conta), conferindo o valor pago com o projetado e gravando as
diferenças como ajuste.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. O usuário tem o CSV de pagamentos do ERP (separador `;`) com as colunas
   `Docto`, `Vencimento`, `Valor Pago` e `Data Pagamento`.

## Pos-condicoes

- Uma liquidação (origem ERP) por parcela confirmada, com lote, nome do
  arquivo, Doctos e quantidade de linhas do ERP; parcelas LIQUIDADAS.
- Um log `CONCILIACAO_ERP` por lote (resumo da prévia, liquidações gravadas,
  total de ajustes).
- O relatório do ERP **não é guardado** (DA09).

## Fluxo principal

1. Em **Operacional > Liquidação**, o usuário filtra as parcelas e,
   opcionalmente, marca algumas; aciona **Importar ERP**.
2. Contratos considerados: os das parcelas marcadas ou, sem marcação, todos os
   filtrados (um grupo entra se tiver ao menos um contrato considerado).
3. O usuário envia o CSV; o sistema lê e valida o arquivo em memória
   (cp1252/utf-8, números e datas no formato brasileiro, linhas sem Docto
   descartadas).
4. Prévia: numa transação desfeita, o sistema carrega o arquivo numa tabela
   temporária e cruza com a projeção (RN22, RN23), mostrando por chave:
   Situação, Contrato, Códigos ERP, Vínculo, Competência, Parcela, Doctos,
   Linhas, Data pagamento, Valor ERP, Valor Nexus e Diferença, e o resumo por
   situação.
5. Conciliado e Diferença vêm marcados; o usuário revisa e aciona
   **Confirmar**.
6. Numa transação gravada, o sistema refaz a conciliação, grava as
   liquidações das linhas marcadas que continuam Conciliado/Diferença (grupo:
   valor rateado proporcionalmente) e o log, e informa as parcelas liquidadas,
   o total de ajustes e as descartadas por mudança desde a prévia.

## Fluxos alternativos

### FA01 - Vincular códigos do ERP

1. Na seção **Vincular códigos do ERP**, o usuário escolhe um código não
   identificado e um ou mais contratos (os "Não pago no ERP" do arquivo vêm
   primeiro, com ★) e aciona **Adicionar**; a lista de pendentes pode ser
   editada.
2. **Vincular** grava todos os pendentes (log `VINCULO_ERP_INCLUIR`) e refaz a
   prévia sem fechar o modal. O vínculo é permanente.

### FA02 - Remover vínculo

Em **Vínculos usados neste arquivo**, o usuário seleciona e remove vínculos
(log `VINCULO_ERP_EXCLUIR`).

### FA03 - Reimportação

Parcelas já liquidadas aparecem como Já liquidada e não podem ser marcadas.

## Situações da prévia

| Situação | Regra | Ao confirmar |
|---|---|---|
| Diferença | Chave casou, valor diferente | Liquida com ajuste |
| Conciliado | Chave casou, mesmo valor | Liquida com ajuste 0 |
| Vínculo conflitante | Parcela em mais de um grupo no mês | Nada |
| Não identificado no Nexus | Código desconhecido ou contrato sem parcela no mês | Nada |
| Não pago no ERP | Parcela aberta de contrato considerado, sem linha no ERP | Nada |
| Já liquidada | Parcela já liquidada | Nada |
| Fora da seleção | Contrato existe, mas não foi considerado | Nada |

## Fluxos de exceção

### FE01 - Arquivo inválido

Coluna obrigatória ausente, data ou valor inválido (com o número da linha):
o arquivo é recusado, nada é gravado.

### FE02 - Mudança entre a prévia e a confirmação

Chaves que deixaram de ser Conciliado/Diferença são descartadas e informadas.

## Regras de negócio

- RN22 (chave e soma), RN23 (vínculos e grupos), RN19/RN20 (liquidação e
  ajuste), RN12 (log por lote).
- Datas de pagamento diferentes somadas na mesma chave: vale a maior (aviso
  na prévia).
- Antecipações e quitações que vierem no relatório do ERP não são tratadas
  (backlog).

## Implementação

- `src/views/liquidacao.py`, `src/views/components/modal_liquidacao_importar.py`
- `src/services/liquidacao.py`, `src/queries/queries_liquidacao.py`
  (`CTE_CONCILIACAO_ERP`)
