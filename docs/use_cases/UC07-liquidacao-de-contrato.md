# UC07 - Liquidação de Parcelas

**Status:** Implementado
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.2, RF09, RN19, RN20, RN21, RN12

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc07---liquidação-de-parcelas)

> Até 10/2026 este UC estava consolidado no UC06 (a "liquidação" era a
> quitação do contrato). A quitação continua no UC06; este UC passou a tratar
> a **baixa das parcelas** com o valor efetivamente pago. A conciliação com o
> relatório do ERP está no [UC13](UC13-conciliacao-erp.md).

## Objetivo

Registrar o pagamento real de cada parcela projetada (liquidação), gravando a
diferença para o valor projetado como ajuste, e permitir desfazer uma
liquidação por estorno.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. A projeção do contrato existe em `financiamento.projecao_parcelas` (DA08).
3. A parcela a liquidar está ABERTA (não liquidada nem cancelada por quitação).

## Pos-condicoes

- Liquidação: um registro em `financiamento.liquidacao` por parcela, com valor
  projetado (cópia do momento da baixa), valor pago e ajuste; a parcela passa a
  LIQUIDADA e o controle do contrato é atualizado.
- Estorno: a liquidação fica marcada como estornada (com motivo, data e
  usuário); a parcela volta a ABERTA e o contrato é recalculado.
- Log de auditoria `LIQUIDACAO_INCLUIR` / `LIQUIDACAO_ESTORNAR` gravado na
  mesma transação.

## Fluxo principal - Liquidar manualmente

1. O usuário acessa **Operacional > Liquidação**.
2. O sistema lista as parcelas do mês atual (filtros por Empresa e Banco —
   seleção entre os cadastros, com **Todos** —, Contrato (busca parcial),
   Vcto de/até e Situação; prefixo `fl_`), com resumo de parcelas,
   liquidadas, projetado, pago e ajustes.
3. O usuário marca uma ou mais parcelas ABERTAS e aciona **Liquidar**.
4. O sistema abre o modal com os dados atuais das parcelas (lidos do banco),
   sugerindo data de pagamento = vencimento e valor pago = valor projetado.
5. O usuário ajusta data e valor pago e aciona **Confirmar**.
6. O sistema valida (data preenchida e não futura; valor maior que zero),
   grava todas as liquidações numa única transação com log de cada uma e
   informa "N parcela(s) liquidada(s)".

## Fluxos alternativos

### FA01 - Estornar liquidação

1. O usuário marca uma ou mais parcelas LIQUIDADAS e aciona **Estornar**.
2. O sistema mostra as liquidações e exige o motivo do estorno.
3. Ao **Confirmar**, as liquidações são estornadas numa única transação; as
   parcelas voltam a ABERTA e os contratos são recalculados.

### FA02 - Liquidar pelo relatório do ERP

Ver [UC13 - Conciliação com o ERP](UC13-conciliacao-erp.md).

## Fluxos de exceção

### FE01 - Seleção inválida

Sem seleção, ou com parcelas que não estão na situação esperada, o sistema
avisa e não abre o modal.

### FE02 - Validação

Data vazia ou futura, valor zerado ou motivo de estorno vazio: o aviso
aparece dentro do modal, que permanece aberto com o que foi editado.

### FE03 - Parcela já liquidada por outra pessoa

O banco recusa (parcela não está ABERTA); nada é gravado e a mensagem do banco
é exibida.

## Regras de negócio

- RN19: só parcelas ABERTAS são liquidadas; o recálculo nunca altera parcela
  liquidada; quitação que cancelaria parcela liquidada é recusada.
- RN20: o ajuste não altera o saldo devedor.
- RN21: liquidação só é estornada (alteração, exclusão e TRUNCATE bloqueados);
  contrato com liquidação não pode ser excluído.
- RN12: inclusão e estorno são registrados no log de auditoria.

## Dados

`financiamento.liquidacao` (ver [Dicionário de Dados](../architecture/data-dictionary.md))
e `financiamento.projecao_parcelas.situacao`.
