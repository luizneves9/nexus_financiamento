# UC08 - Atualização da Selic

**Status:** Implementado (importação sob demanda; agendamento planejado)
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF01, RN02, RN04, RN05, RN25

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc08---atualização-da-selic)

## Objetivo

Manter no banco a série oficial da Selic (fator UM143 do BNDES), usada no
cálculo da projeção, dos contratos e das antecipações.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. O servidor tem acesso a `https://www.bndes.gov.br/Moedas/um143.txt`.

## Pos-condicoes

- As datas posteriores à última gravada são inseridas em `financiamento.selic`
  num único comando.
- O trigger da Selic recalcula, uma vez por importação, os contratos com
  parcelas abertas afetadas (DA08).
- Log `SELIC_IMPORTAR` com quantidade, primeira e última data, fonte e
  contratos recalculados.

## Fluxo principal

1. O usuário acessa **Cadastros > Selic**.
2. O sistema lista os valores gravados (filtro opcional por período; prefixo
   `fs_`), com resumo de registros, primeira e última data.
3. O usuário aciona **Atualizar Selic (BNDES)**.
4. O sistema baixa o arquivo, ignora cabeçalho e linhas vazias e converte data
   (dd/mm/aaaa) e valor (vírgula decimal).
5. O sistema grava só as datas posteriores à última data gravada e informa
   "N nova(s) data(s) de Selic importada(s), de dd/mm a dd/mm; X contrato(s)
   recalculado(s)."

## Fluxos alternativos

### FA01 - Selic já atualizada

O sistema informa "Selic já está atualizada (última data: dd/mm/aaaa)".

### FA02 - Datas antigas ausentes

Datas da série do BNDES anteriores à última gravada que não estão no banco
não são importadas; o sistema apenas informa a quantidade.

## Fluxos de exceção

### FE01 - Site indisponível ou sem acesso à internet

Nada é gravado; a falha é registrada no log e exibida ao usuário.

### FE02 - Arquivo em formato inesperado

A importação é recusada indicando a linha; nada é gravado.

## Regras de negócio

- RN25: série oficial do BNDES; só datas novas.
- RN04 / RN05: a Selic do contrato e da antecipação é a última disponível até
  a data BNDES / data de tesouraria (triggers existentes).
- O BNDES publica a Selic com antecedência (ex.: o dia seguinte); essas datas
  também são importadas.

## Histórico

Em 16/10/2026 a tabela foi recarregada a partir da série oficial: as cargas
manuais por planilha tinham gravado datas com dia e mês trocados (dias até 12).
Backup da tabela anterior em `financiamento_base.selic_backup_20261016`
(até a limpeza final).
