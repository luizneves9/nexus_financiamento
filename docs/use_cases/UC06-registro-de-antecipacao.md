# UC06 - Antecipação e Liquidação Antecipada de Contrato

**Status:** Implementado para contratos BNDES FINAME SELIC
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF07.1, RN02, RN05, RN09, RN10, RN13, RN14, RN15

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc06---antecipação-e-liquidação-antecipada-de-contrato)

> Este Use Case consolida o que antes era tratado separadamente em UC06
> (Registro de Antecipação) e UC07 (Liquidação de Contrato). Antecipação
> parcial e quitação total de um contrato usam o mesmo fluxo, o mesmo modal e
> a mesma tabela (`financiamento.antecipacao`), diferenciados apenas pelo
> campo `tipo_lancamento`. UC07 permanece como registro histórico e aponta
> para este documento.

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
   tipo `BNDES FINAME SELIC` (única modalidade presente em
   `mv_projecao_moeda` nesta versão — ver RN15).

## Pos-condicoes

- O registro é persistido em `financiamento.antecipacao`, com
  `tipo_lancamento` igual a `ANTECIPACAO` ou `QUITACAO`.
- A trigger `trg_processar_dados_antecipacao` (`BEFORE INSERT OR UPDATE`)
  calcula a Selic e o `valor_moeda` do registro antes de gravar.
- A trigger `trg_after_insert_antecipacao` (`AFTER INSERT`) aciona
  `refresh_views_contratos()`, recalculando `mv_projecao_moeda`,
  `mv_projecao_moeda_final` e `mv_projecao_tfc`.
- Quando `tipo_lancamento = QUITACAO`, a projeção do contrato é truncada na
  parcela da quitação (ver `docs/architecture/financial-calculation.md`).
- O sistema notifica o resultado da operação ao usuário.

## Fluxo principal

1. O usuário, na tela de Gestão de Contratos, seleciona exatamente um
   contrato e aciona o botão **Liquidar**.
2. O sistema abre um modal com os dados do contrato preenchidos
   automaticamente: id, número do contrato, empresa, banco, valor
   financiado, data de emissão e data de vencimento.
3. O usuário informa a **Data de Pagamento** e aciona o botão **Calcular
   Saldo Devedor**.
4. O sistema busca, em `mv_projecao_moeda`, a parcela com vencimento maior
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
   e a trigger `trg_after_insert_antecipacao` atualiza as materialized
   views.
10. O sistema informa o sucesso do registro.

O botão **Cancelar** fecha o modal sem persistir nada.

## Fluxos de exceção

### FE01 - Contrato inexistente

A chave estrangeira impede o registro.

### FE02 - Contrato sem parcelas em `mv_projecao_moeda`

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

## Evidência

- `src/views/contracts.py` (botão **Liquidar**).
- `src/views/components/modal_liquidacao_antecipacao.py` (modal).
- `src/services/liquidacao_antecipacao.py` (orquestração e validações).
- `src/queries/queries_antecipacao.py` (consultas SQL).
