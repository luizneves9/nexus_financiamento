# Roadmap

O detalhamento de cada pendência, sua evidência e o critério de conclusão
está no [Registro de Status e Pendências](requirements/status-register.md).

## Fase atual - Desenvolvimento

- Inclusão e consulta de contratos.
- Consulta de empresas, bancos e fornecedores.
- Visualização parcial de projeções.
- Projeção persistida por contrato, com recálculo automático (DA08), no
  lugar das materialized views.
- Relatório Contas a Pagar (Relatórios > Contas a Pagar) na posição da data
  base, com filtros, resumo e exportação para Excel.
- Consulta de antecipações e quitações (Operacional > Antecipação), com
  filtros e resumo.
- Autenticação: login, cadastro de senha no primeiro acesso, sessão de 30
  minutos e Sair (UC12).
- Log de auditoria de escritas e eventos de acesso (RF08.1).
- Relatório de endividamento com fluxo de caixa (Relatórios > Endividamento)
  na posição da data base, com Financiamentos, Compra Santo Anjo, Consórcios e
  Tributário, créditos de consórcio, Dívida Líquida, resumo do mês (variação)
  e tema automático/manual, ainda sem download e em calibração (selo BETA).
- Consórcio (Operacional > Consórcio, UC16): importação dos CSVs pago e a
  pagar e créditos do fechamento.
- Outros pagamentos (Operacional > Outros Pagamentos, UC17): parcelas de
  Compra Santo Anjo e Tributário com baixa e estorno.
- Data de contabilização do contrato (RN28), que define a entrada no
  Endividamento e no Painel sem afetar a projeção.
- Exclusão física de contratos.
- Estruturas de banco para bens e veículos.
- Importação da Selic do BNDES (Cadastros > Selic, UC08).
- Identidade visual compartilhada com o Nexus Extrato (DA07/RNF15).
- Quitação/Antecipação de contrato (UC06), para contratos BNDES FINAME
  SELIC, com exclusão de lançamento.
- Liquidação de parcelas manual e estorno (UC07) e conciliação com o
  relatório de pagamentos do ERP, com vínculos ERP → Nexus (UC13).
- Detalhe do contrato em abas, com anexos (PDF) de contrato e ficha
  financeira no banco e visualização na tela (UC14).
- Painel de indicadores (Painel > Indicadores, tela inicial) comparando dois
  anos (Data X × Data Y), com fluxo de pagamentos mensal e composição (UC15).

## Versão 1.0

- Completar cadastro e vínculo de bens e veículos.
- Suportar, na quitação/antecipação, contratos de modalidades
  além de BNDES FINAME SELIC.
- Resolver as pendências de segurança da autenticação: `.env` fora do Git e
  segredos rotacionados (BL-014), HTTPS (BL-015), limite de tentativas
  (BL-016) e invalidação de sessões (BL-017).
- Implementar perfis e permissões por aba e ação (BL-005), registrando
  `ACESSO_NEGADO` no log.
- Implementar filtros e detalhamento.
- Adicionar download ao relatório de Endividamento (BL-011).
- Validar Endividamento, resumo do mês e Painel com o financeiro e retirar o
  selo BETA (BL-033, BL-031).
- Tela de edição de contratos (data de contabilização e dados cadastrais,
  com log) (BL-032).
- Validar cálculos com testes de banco e aceite do financeiro.
- Agendar a importação da Selic (BL-030).
- Corrigir os bugs de cálculo herdados das materialized views (BL-027).

## Evolucoes posteriores

- Avaliar exclusão lógica.
- Tela de consulta do histórico de auditoria (BL-021) e política de
  retenção do log (BL-022).
- Definir aprovação por perfil para ajustes e baixas.
- Formalizar backup, restauração, RTO e RPO.
- Aprimorar regras de unicidade de chassi e placa.
- Tela de cadastro dos vínculos ERP → Nexus (BL-029) e tratamento de
  antecipações vindas no relatório do ERP (BL-028).

## Critério de conclusão da versão 1.0

A versão 1.0 será considerada pronta quando os fluxos prioritários estiverem
implementados na interface, persistidos corretamente, cobertos por testes,
protegidos por acesso adequado e aprovados pelo responsável do negócio.
