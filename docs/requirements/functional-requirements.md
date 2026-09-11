# Requisitos Funcionais

## Escopo

Este documento define os comportamentos funcionais do Nexus - Gestão de
Financiamentos. O status indica a situação da aplicação, e não apenas a
existência de estruturas correspondentes no banco de dados.

## Requisitos

| ID | Requisito | Descricao | Status |
| --- | --- | --- | --- |
| RF01 | Disponibilização da Selic | Manter valores da Selic no banco e, futuramente, importar dados por API ou job. | Banco disponível; API planejada |
| RF02 | Inclusão de contratos | Permitir o cadastro manual de contratos com dados da empresa, banco, valores, taxas, prazos e cobrança. | Parcialmente implementado |
| RF02.1 | Formulario de contrato | Disponibilizar formulario web com validação dos campos obrigatórios, valores e datas. | Implementado |
| RF02.2 | Vínculo de bens e veículos | Associar bens, chassis e carrocerias a um contrato. | Planejado para a versão 1.0 |
| RF03 | Consulta de contratos | Exibir contratos cadastrados para consulta operacional. | Implementado |
| RF03.1 | Filtros de contratos | Filtrar contratos por banco, taxa, período, valor e tipo. | Planejado |
| RF04 | Consulta de veículos | Exibir bens e veículos associados aos contratos. | Planejado para a versão 1.0 |
| RF04.1 | Filtros de veículos | Filtrar veículos por banco, taxa, período, valor e situação. | Planejado |
| RF05 | Exclusão física de contratos | Remover físicamente um contrato mediante confirmação e respeitando integridade referencial. | Implementado, sujeito a dependências |
| RF06 | Exclusão de veículos | Remover bens ou veículos conforme regras de integridade. | Planejado |
| RF07 | Projeção financeira | Exibir parcelas e valores calculados pelo PostgreSQL. | Parcialmente implementado |
| RF07.1 | Antecipação | Registrar pagamento antecipado e refletir a operação na projeção. | Banco preparado; interface planejada |
| RF07.2 | Liquidação | Simular e registrar liquidação total ou parcial. | Planejado para a versão 1.0 |
| RF08 | Detalhamento e auditoria | Exibir detalhes do registro e histórico de alterações. | Planejado |
| RF09 | Ajustes financeiros | Permitir registrar ajustes financeiros apos o vencimento. | Planejado |
| RF10 | Autenticação e perfis | Controlar acesso por usuário e perfil. | Planejado para a versão 1.0 |

## Critérios gerais de aceite

- Cada requisito implementado deve possuir pelo menos um fluxo de caso de uso
  e um teste correspondente.
- Operacoes de escrita devem confirmar sucesso somente apos a transação no
  PostgreSQL ser concluida.
- Falhas de integridade ou comúnicação devem ser apresentadas ao usuário sem
  confirmar a operação.
- Requisitos planejados somente seráo considerados implementados quando houver
  fluxo na interface, persistência validada e teste registrado.
