# Integracoes

## Estado atual

A aplicação acessa diretamente o PostgreSQL configurado no ambiente e
possui duas integrações de arquivo, descritas abaixo: a série da Selic do
BNDES (download HTTP) e o relatório de pagamentos do ERP (upload de CSV).

## Selic (BNDES)

- Fonte: `https://www.bndes.gov.br/Moedas/um143.txt` (fator UM143), sem
  autenticação.
- Formato: texto com cabeçalho `data;valor`, separador `;` com espaços, data
  `dd/mm/aaaa`, valor com vírgula decimal (6 casas), mais nova primeiro; só
  dias úteis; o BNDES publica alguns dias à frente.
- Coleta: botão **Atualizar Selic (BNDES)** (Cadastros > Selic), timeout de
  30 s, biblioteca padrão (`urllib`).
- Gravação: só datas posteriores à última gravada, num único INSERT; log
  `SELIC_IMPORTAR`; falha registrada e exibida.
- Pendente: agendamento e acesso do servidor de produção (BL-030).

## Relatório de pagamentos do ERP (CSV)

- Upload na tela Liquidação > Importar ERP; o arquivo não é guardado (DA09).
- Separador `;`, codificação utf-8 ou cp1252; cabeçalhos vazios ignorados.
- Colunas obrigatórias: `Docto`, `Vencimento`, `Valor Pago`, `Data Pagamento`
  (opcionais: `Filial`, `Fornecedor`). Números `3.972,07` ou `3972,07`; datas
  `dd/mm/aaaa`; `Histórico` não é usado.
- Chave: Docto antes do primeiro `-` + mês/ano do Vencimento (RN22).

## Itens ainda a definir para a Selic

Para um agendamento automático, a solução deverá definir:

- fonte oficial e endpoint;
- autenticação, caso exigida;
- periodicidade da coleta;
- formato de data e valor;
- tratamento de duplicidade por data;
- retry e comportamento offline;
- logs sem exposicao de credenciais;
- validação dos dados antes da persistência;
- política para indisponibilidade da fonte;
- atualização das estruturas de projeção.

## Responsável operacional

A importação da Selic e a conciliação do ERP são acionadas pelo usuário do
financeiro; o responsável pelo agendamento ainda será definido (BL-030).
