# UC06 - Quitação/Antecipação de Contrato

**Status:** Implementado para contratos BNDES FINAME SELIC
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.1, RN02, RN05, RN09, RN10, RN13, RN14, RN15, RN19

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc06---antecipação-e-liquidação-antecipada-de-contrato)

> Antecipação parcial e quitação total de um contrato usam o mesmo fluxo, o
> mesmo modal e a mesma tabela (`financiamento.antecipacao`), diferenciados
> pelo campo `tipo_lancamento`. Até 10/2026 o botão se chamava "Liquidar"; a
> liquidação (baixa de parcelas pelo valor pago) agora é o
> [UC07](UC07-liquidacao-de-contrato.md).

## Objetivo

Registrar, pela interface, um pagamento antecipado (parcial) ou a quitação
total de um contrato, exibindo ao usuário o saldo devedor e a Selic da data
informada antes da confirmação, e refletir a operação na projeção
financeira.

## Pre-condicoes

1. O contrato está cadastrado.
2. O usuário selecionou exatamente um contrato na tela de Gestão de
   Contratos.
3. Para o cálculo de saldo devedor pré-confirmação, o contrato deve ser do
   tipo `BNDES FINAME SELIC` (única modalidade atendida pelo cálculo de saldo
   devedor nesta versão — ver RN15).

## Pos-condicoes

- O registro é persistido em `financiamento.antecipacao`, com
  `tipo_lancamento` igual a `ANTECIPACAO` ou `QUITACAO`.
- A trigger `trg_processar_dados_antecipacao` (`BEFORE INSERT OR UPDATE`)
  calcula a Selic e o `valor_moeda` do registro antes de gravar.
- A trigger `trg_projecao_antecipacao` (`AFTER INSERT OR UPDATE OR DELETE`)
  recalcula a projeção só do contrato do lançamento (DA08).
- Quando `tipo_lancamento = QUITACAO`, as parcelas a partir da parcela da
  quitação ficam como `CANCELADA_QUITACAO` (ver
  `docs/architecture/financial-calculation.md`).
- O sistema notifica o resultado da operação ao usuário.

## Fluxo principal

1. O usuário, na tela de Gestão de Contratos, seleciona exatamente um
   contrato e aciona o botão **Quitação/Antecipação**.
2. O sistema abre um modal com os dados do contrato preenchidos
   automaticamente: id, número do contrato, empresa, banco, valor
   financiado, data de emissão e data de vencimento.
3. O usuário informa a **Data de Pagamento** e aciona o botão **Calcular
   Saldo Devedor**.
4. O sistema busca, em `projecao_parcelas` (sem as parcelas canceladas por
   quitação), a parcela com vencimento maior
   ou igual à data de pagamento mais próxima (ou a última parcela do
   contrato, se não houver parcela futura), busca a Selic exata da data
   informada ou a próxima disponível (ou a mais recente cadastrada, se não
   houver data futura) e calcula o saldo devedor em moeda multiplicando o
   saldo devedor da parcela pela Selic encontrada. O sistema exibe Saldo
   Devedor, Data Selic e Valor Selic.
5. O usuário seleciona o **Tipo de Lançamento** (`ANTECIPACAO` ou
   `QUITACAO`), informa o **Valor do Boleto**, a **Data Tesouraria** e a
   **Data de Compensação**.
6. O usuário aciona **Confirmar**.
7. O sistema valida os campos obrigatórios, a regra de quitação única
   (RN13) e a ordem das datas (RN14).
8. O sistema grava o registro em `financiamento.antecipacao`.
9. A trigger `trg_processar_dados_antecipacao` calcula Selic/valor em moeda
   e a trigger `trg_projecao_antecipacao` recalcula a projeção do contrato.
10. O sistema informa o sucesso do registro.

O botão **Cancelar** fecha o modal sem persistir nada.

## Fluxos de exceção

### FE01 - Contrato inexistente

A chave estrangeira impede o registro.

### FE02 - Contrato que não é BNDES FINAME SELIC

Quando o contrato não é do tipo `BNDES FINAME SELIC`, a busca de parcelas
retorna vazia e o sistema informa que a funcionalidade atende apenas essa
modalidade (RN15), sem calcular saldo devedor.

### FE03 - Selic indisponível

Quando não existe nenhuma Selic cadastrada no banco, o sistema informa o
erro e não calcula o saldo devedor em moeda.

### FE04 - Quitação já existente

Quando o contrato já possui um lançamento `QUITACAO`, o sistema bloqueia o
registro de uma nova quitação (RN13).

### FE05 - Datas fora de ordem

Quando a data de tesouraria é anterior à data de pagamento, ou a data de
compensação é anterior à data de tesouraria, o sistema bloqueia o registro
(RN14).

### FE06 - Falha de persistência

O sistema informa o erro e não confirma o registro.

### FE07 - Quitação que cancelaria parcela liquidada

O recálculo recusa a operação (RN19) e nada é gravado.

## Fluxo alternativo FA01 - Excluir lançamento

1. Em **Operacional > Antecipação**, o usuário seleciona exatamente um
   lançamento e aciona **Excluir**.
2. O modal mostra o lançamento e avisa que a projeção será recalculada.
3. Ao **Confirmar**, o lançamento é excluído (log `ANTECIPACAO_EXCLUIR` com a
   cópia do registro) e o trigger recalcula o contrato.

## Regras de negócio

- A antecipação ou quitação pertence a um contrato (RN08).
- A Selic e procurada a partir da data de pagamento informada (RN05).
- O saldo devedor exibido no modal e calculado pela multiplicação do saldo
  devedor da parcela pela Selic da data (RN02).
- O registro deve ser efetivo, e não apenas uma simulação (RN09).
- Um contrato não pode ter mais de uma quitação (RN13).
- A ordem das datas de pagamento, tesouraria e compensação deve ser
  respeitada (RN14).
- O cálculo de saldo devedor pré-confirmação está limitado a contratos
  BNDES FINAME SELIC (RN15).

## Auditoria

O registro grava `ANTECIPACAO_INCLUIR` ou `QUITACAO_INCLUIR` (conforme o tipo de lançamento) em `financiamento.log_auditoria` na mesma transação do lançamento, com contrato, datas, valor e tipo em `detalhes`. Falhas são registradas com `sucesso = false` e o erro (RF08.1, RN12).

## Evidência

- `src/views/contracts.py` (botão **Quitação/Antecipação**).
- `src/views/components/modal_quitacao_antecipacao.py` (modal).
- `src/services/quitacao_antecipacao.py` (orquestração e validações).
- `src/views/include_antecipation.py`, `src/views/components/modal_antecipacao_excluir.py`
  e `src/services/include_antecipation.py` (exclusão).
- `src/queries/queries_antecipacao.py` (consultas SQL).
