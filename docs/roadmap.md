# Roadmap

O detalhamento de cada pendência, sua evidência e o critério de conclusão
está no [Registro de Status e Pendências](requirements/status-register.md).

## Fase atual - Desenvolvimento

- Inclusão e consulta de contratos.
- Consulta de empresas, bancos e fornecedores.
- Visualização parcial de projeções.
- Relatório consolidado de projeção de pagamentos (Relatórios > Projeção de
  Pagamentos), ainda sem filtros nem download.
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
- Implementar autenticação e perfis.
- Implementar filtros e detalhamento.
- Adicionar filtros e download de arquivos à tela consolidada de projeções
  (Relatórios > Projeção de Pagamentos).
- Validar cálculos com testes de banco e aceite do financeiro.
- Definir integração da Selic por API ou job.

## Evolucoes posteriores

- Avaliar exclusão lógica.
- Implementar auditoria completa.
- Definir aprovação por perfil para ajustes e baixas.
- Formalizar backup, restauração, RTO e RPO.
- Aprimorar regras de unicidade de chassi e placa.
- Automatizar atualização das matérialized views apos operações relevantes.

## Critério de conclusão da versão 1.0

A versão 1.0 será considerada pronta quando os fluxos prioritários estiverem
implementados na interface, persistidos corretamente, cobertos por testes,
protegidos por acesso adequado e aprovados pelo responsável do negócio.
