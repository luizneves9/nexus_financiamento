# UC14 - Detalhe do Contrato e Anexos

**Status:** Implementado
**Ator principal:** Usuario responsável pelo setor financeiro
**Requisitos associados:** RF03.1, RF03.2, RN26, RN12

**Rastreamento detalhado:** [Registro de Status e Pendências](../requirements/status-register.md#uc14---detalhe-do-contrato-e-anexos)

## Objetivo

Consultar um contrato num único lugar (dados, documentos e histórico) e
centralizar no sistema os PDFs do contrato e da ficha financeira.

## Pre-condicoes

1. O usuário está autenticado (UC12).
2. O usuário selecionou exatamente um contrato em **Operacional > Contratos**.

## Pos-condicoes

- Anexos incluídos ficam em `financiamento.anexo_contrato` ou
  `financiamento.anexo_ficha_financeira` (o PDF dentro do banco), com log
  `ANEXO_INCLUIR`; anexos excluídos são removidos com log `ANEXO_EXCLUIR`.
- As colunas **Anexo contrato** e **Anexo ficha** da lista refletem os anexos.

## Fluxo principal

1. Na lista de contratos, o usuário seleciona um contrato e aciona
   **Detalhes**.
2. O sistema abre o modal **Detalhe do contrato**: número do contrato,
   "Empresa · Banco · Situação" e as abas:
   - **Dados** — campos do contrato (tipo, datas, valor, Selic, taxas,
     prazos, registro de cobrança, situação e parcelas liquidadas);
   - **Contrato** e **Ficha Financeira** — escolha do arquivo, PDF exibido na
     tela (visualizador do navegador, com o link "Abrir em nova aba"),
     **Baixar**, **Excluir** e inclusão de novos PDFs (**Anexar**);
   - **Histórico** — ações do log de auditoria ligadas ao contrato
     (inclusão, antecipações/quitações, liquidações, estornos, anexos).
3. Ao fechar o modal (X), a lista de contratos é atualizada.

## Fluxos alternativos

### FA01 - Anexar PDFs

1. Na aba Contrato ou Ficha Financeira, o usuário seleciona um ou mais PDFs
   e aciona **Anexar**.
2. O sistema valida (RN26) e grava todos numa transação, com log de cada
   arquivo; o modal continua aberto na mesma aba.

### FA02 - Excluir anexo

O usuário aciona **Excluir** no arquivo selecionado e confirma; o anexo é
removido na hora, com log.

### FA03 - Filtrar contratos sem anexos

Na lista, o checkbox **Somente sem anexos** (desmarcado por padrão) mostra os
contratos sem anexo de contrato ou sem anexo de ficha financeira.

## Fluxos de exceção

### FE01 - Arquivo inválido

Arquivo que não é PDF, vazio ou acima de 20 MB: nada é gravado e o aviso
aparece no modal.

### FE02 - PDF já anexado

O mesmo arquivo (mesmo hash) no mesmo contrato e tipo é recusado; nada é
gravado.

### FE03 - Seleção inválida

Sem exatamente um contrato selecionado, o sistema avisa e não abre o modal.

## Regras de negócio

- RN26: anexos.
- RN12: inclusão e exclusão de anexos registradas no log; o conteúdo do PDF
  nunca vai para o log. A exclusão do contrato remove os anexos junto e
  registra seus nomes no log `CONTRATO_EXCLUIR`.
- O modal só consulta (Dados, Histórico) e não gera log por consulta.

## Implementação

- `src/views/components/modal_contracts_detalhe.py` (abas; uma função por aba
  — novas funcionalidades entram como novas abas)
- `src/views/components/visualizador_pdf.py` (PDF na página principal: o
  Chrome/Edge bloqueiam o visualizador de PDF dentro de iframes isolados,
  como os do `st.iframe`)
- `src/services/anexos.py`, `src/queries/queries_anexos.py`
- `database/contrato_anexos.sql`
