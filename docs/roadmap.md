# Roadmap

O detalhamento de cada pendência, sua evidência e o critério de conclusão
está no [Registro de Status e Pendências](requirements/status-register.md).

## Fase atual - Desenvolvimento

- Inclusão e consulta de contratos.
- Consulta de empresas, bancos e fornecedores.
- Visualização parcial de projeções.
- Relatório consolidado de projeção de pagamentos (Relatórios > Projeção de
  Pagamentos), com filtros e resumo, ainda sem download.
- Consulta de antecipações e quitações (Operacional > Antecipação), com
  filtros e resumo.
- Autenticação: login, cadastro de senha no primeiro acesso, sessão de 30
  minutos e Sair (UC12).
- Log de auditoria de escritas e eventos de acesso (RF08.1).
- Relatório de endividamento com fluxo de caixa (Relatórios > Endividamento),
  com tema automático/manual, ainda sem filtros nem download.
- Exclusão física de contratos.
- Estruturas de banco para Selic, bens e veículos.
- Antecipação e liquidação antecipada de contrato (UC06), para contratos
  BNDES FINAME SELIC.

## Versão 1.0

- Completar cadastro e vínculo de bens e veículos.
- Suportar, na antecipação/liquidação antecipada, contratos de modalidades
  além de BNDES FINAME SELIC.
- Resolver as pendências de segurança da autenticação: `.env` fora do Git e
  segredos rotacionados (BL-014), HTTPS (BL-015), limite de tentativas
  (BL-016) e invalidação de sessões (BL-017).
- Implementar perfis e permissões por aba e ação (BL-005), registrando
  `ACESSO_NEGADO` no log.
- Implementar filtros e detalhamento.
- Adicionar download de arquivos à tela consolidada de projeções
  (Relatórios > Projeção de Pagamentos); filtros já entregues.
- Validar cálculos com testes de banco e aceite do financeiro.
- Definir integração da Selic por API ou job.

## Evolucoes posteriores

- Avaliar exclusão lógica.
- Tela de consulta do histórico de auditoria (BL-021) e política de
  retenção do log (BL-022).
- Definir aprovação por perfil para ajustes e baixas.
- Formalizar backup, restauração, RTO e RPO.
- Aprimorar regras de unicidade de chassi e placa.
- Automatizar atualização das matérialized views apos operações relevantes.

## Critério de conclusão da versão 1.0

A versão 1.0 será considerada pronta quando os fluxos prioritários estiverem
implementados na interface, persistidos corretamente, cobertos por testes,
protegidos por acesso adequado e aprovados pelo responsável do negócio.
