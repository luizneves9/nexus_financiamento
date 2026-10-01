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
| RF02.3 | Projeção durante a inclusão | Permitir solicitar a projeção antes da gravação definitiva, exibindo o resultado no mesmo modal do formulário. | Implementado |
| RF02.2 | Vínculo de bens e veículos | Associar bens, chassis e carrocerias a um contrato. | Planejado para a versão 1.0 |
| RF03 | Consulta de contratos | Exibir contratos cadastrados para consulta operacional. | Implementado |
| RF03.1 | Filtros de contratos | Filtrar contratos por empresa, banco e número (busca parcial). Filtros adicionais (taxa, período, valor, tipo) planejados para evolução. | Parcialmente implementado |
| RF04 | Consulta de veículos | Exibir bens e veículos associados aos contratos. | Planejado para a versão 1.0 |
| RF04.1 | Filtros de veículos | Filtrar veículos por banco, taxa, período, valor e situação. | Planejado |
| RF05 | Exclusão física de contratos | Remover físicamente um contrato mediante confirmação e respeitando integridade referencial. | Implementado, sujeito a dependências |
| RF06 | Exclusão de veículos | Remover bens ou veículos conforme regras de integridade. | Planejado |
| RF07 | Projeção financeira | Exibir parcelas e valores calculados pelo PostgreSQL. | Parcialmente implementado |
| RF07.1 | Antecipação e liquidação antecipada de contrato | Registrar, em um único fluxo, a antecipação (pagamento parcial) ou a quitação total de um contrato, calculando saldo devedor e Selic da data informada antes da confirmação e refletindo a operação na projeção. | Implementado para contratos BNDES FINAME SELIC |
| RF07.2 | Liquidação | Consolidado em RF07.1: a quitação total é registrada como um tipo de lançamento (`QUITACAO`) na mesma tela de antecipação, sem fluxo ou estrutura de dados próprios. Ver UC06. | Consolidado em RF07.1 |
| RF07.3 | Relatório de projeção de pagamentos | Exibir, em Relatórios, o agrupamento consolidado da projeção de pagamentos de todos os contratos, com filtros por Empresa, Banco, Contrato (busca parcial) e intervalo de Data de Vencimento aplicados no banco, e resumo abaixo da tabela (quantidade de empresas, bancos e contratos e total das parcelas). Exportação/download planejada. | Implementado (sem exportação) |
| RF07.4 | Relatório de endividamento | Exibir, em Relatórios, a projeção de pagamentos agrupada por ano e mês em um formato de tabela consolidada (fluxo de caixa), com suporte a tema claro/escuro automático. | Implementado |
| RF07.5 | Consulta de antecipações | Exibir, em Operacional > Antecipação, todas as antecipações e quitações registradas (id, empresa, banco, contrato, data de pagamento, valor pago e tipo de lançamento), com filtros por Empresa, Banco, Contrato (busca parcial) e intervalo de Data de Pagamento aplicados no banco, e resumo abaixo da tabela (quantidade de empresas, bancos e contratos e total pago). | Implementado |
| RF08 | Detalhamento e auditoria | Exibir detalhes do registro e histórico de alterações. | Parcialmente implementado |
| RF08.1 | Log de auditoria | Registrar em `financiamento.log_auditoria` cada operação de escrita (inclusão e exclusão de contrato, antecipação/quitação, cadastro de senha) e cada evento de acesso (login, falha de login, logout, sessão encerrada), com usuário, data/hora, ação, registro afetado, resultado, detalhes e IP. O log de uma escrita é gravado na mesma transação da operação; falhas também são registradas. O log é somente inserção. | Implementado |
| RF08.2 | Consulta do histórico | Exibir na interface o histórico de operações de um registro e do sistema, a partir do log de auditoria. | Planejado |
| RF09 | Ajustes financeiros | Permitir registrar ajustes financeiros apos o vencimento. | Planejado |
| RF10 | Autenticação e perfis | Controlar acesso por usuário e perfil. | Parcialmente implementado (autenticação implementada; perfis planejados) |
| RF10.1 | Login | Exigir usuário e senha antes de exibir qualquer tela do sistema; credenciais validadas em `financiamento.usuarios`. Erros exibem notificação genérica ("Usuário ou senha incorretos."), sem revelar se o usuário existe. Botão **Sair** na barra lateral encerra a sessão e recarrega a página. | Implementado |
| RF10.2 | Cadastro de senha no primeiro acesso | Usuário criado pelo desenvolvedor sem senha entra com a senha vazia e cadastra a própria senha (mínimo de 8 caracteres, com confirmação); a senha é gravada somente como hash. | Implementado |
| RF10.3 | Permanência da sessão | Manter o usuário logado por 30 minutos após o último uso, inclusive ao fechar e reabrir o navegador; usuário bloqueado ou com senha resetada perde o acesso. | Implementado |
| RF10.4 | Perfis e permissões | Controlar, por perfil, quais abas cada usuário visualiza e quais ações (ex.: exclusão) pode executar. | Planejado para a versão 1.0 |

## Critérios gerais de aceite

- Cada requisito implementado deve possuir pelo menos um fluxo de caso de uso
  e um teste correspondente.
- Operacoes de escrita devem confirmar sucesso somente apos a transação no
  PostgreSQL ser concluida.
- Falhas de integridade ou comúnicação devem ser apresentadas ao usuário sem
  confirmar a operação.
- Requisitos planejados somente seráo considerados implementados quando houver
  fluxo na interface, persistência validada e teste registrado.
