# Requisitos Funcionais

## Escopo

Este documento define os comportamentos funcionais do Nexus - Gestao de
Financiamentos. O status indica a situacao da aplicacao, e nao apenas a
existencia de estruturas correspondentes no banco de dados.

## Requisitos

| ID | Requisito | Descricao | Status |
| --- | --- | --- | --- |
| RF01 | Disponibilizacao da Selic | Manter valores da Selic no banco e, futuramente, importar dados por API ou job. | Banco disponivel; API planejada |
| RF02 | Inclusao de contratos | Permitir o cadastro manual de contratos com dados da empresa, banco, valores, taxas, prazos e cobranca. | Parcialmente implementado |
| RF02.1 | Formulario de contrato | Disponibilizar formulario web com validacao dos campos obrigatorios, valores e datas. | Implementado |
| RF02.2 | Vinculo de bens e veiculos | Associar bens, chassis e carrocerias a um contrato. | Planejado para a versao 1.0 |
| RF03 | Consulta de contratos | Exibir contratos cadastrados para consulta operacional. | Implementado |
| RF03.1 | Filtros de contratos | Filtrar contratos por banco, taxa, periodo, valor e tipo. | Planejado |
| RF04 | Consulta de veiculos | Exibir bens e veiculos associados aos contratos. | Planejado para a versao 1.0 |
| RF04.1 | Filtros de veiculos | Filtrar veiculos por banco, taxa, periodo, valor e situacao. | Planejado |
| RF05 | Exclusao fisica de contratos | Remover fisicamente um contrato mediante confirmacao e respeitando integridade referencial. | Implementado, sujeito a dependencias |
| RF06 | Exclusao de veiculos | Remover bens ou veiculos conforme regras de integridade. | Planejado |
| RF07 | Projecao financeira | Exibir parcelas e valores calculados pelo PostgreSQL. | Parcialmente implementado |
| RF07.1 | Antecipacao | Registrar pagamento antecipado e refletir a operacao na projecao. | Banco preparado; interface planejada |
| RF07.2 | Liquidacao | Simular e registrar liquidacao total ou parcial. | Planejado para a versao 1.0 |
| RF08 | Detalhamento e auditoria | Exibir detalhes do registro e historico de alteracoes. | Planejado |
| RF09 | Ajustes financeiros | Permitir registrar ajustes financeiros apos o vencimento. | Planejado |
| RF10 | Autenticacao e perfis | Controlar acesso por usuario e perfil. | Planejado para a versao 1.0 |

## Criterios gerais de aceite

- Cada requisito implementado deve possuir pelo menos um fluxo de caso de uso
  e um teste correspondente.
- Operacoes de escrita devem confirmar sucesso somente apos a transacao no
  PostgreSQL ser concluida.
- Falhas de integridade ou comunicacao devem ser apresentadas ao usuario sem
  confirmar a operacao.
- Requisitos planejados somente serao considerados implementados quando houver
  fluxo na interface, persistencia validada e teste registrado.
