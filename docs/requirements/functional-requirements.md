# Requisitos Funcionais

## Escopo

Este documento define os comportamentos funcionais do Nexus - Gestão de
Financiamentos. O status indica a situação da aplicação, e não apenas a
existência de estruturas correspondentes no banco de dados.

## Requisitos

| ID | Requisito | Descricao | Status |
| --- | --- | --- | --- |
| RF01 | Disponibilização da Selic | Manter os valores da Selic no banco, importados da série oficial do BNDES (UM143) pela tela Cadastros > Selic (botão Atualizar Selic), somente com as datas posteriores à última gravada, e listar tudo o que está gravado com filtro por período. | Implementado (importação manual sob demanda; agendamento planejado) |
| RF02 | Inclusão de contratos | Permitir o cadastro manual de contratos com dados da empresa, banco, valores, taxas, prazos e cobrança. | Parcialmente implementado |
| RF02.1 | Formulario de contrato | Disponibilizar formulario web com validação dos campos obrigatórios, valores e datas. | Implementado |
| RF02.3 | Projeção durante a inclusão | Exibir, na aba Projeção do modal de inclusão, a projeção calculada automaticamente com os dados preenchidos (sem gravar o contrato), ou a lista do que falta preencher. | Implementado |
| RF02.4 | Data de contabilização | Informar, na inclusão do contrato, a data de contabilização (obrigatória, maior ou igual à data de emissão; vem preenchida com a emissão), que define a partir de quando o contrato entra no Endividamento e no Painel (RN28). Não altera a projeção. Exibida no detalhe do contrato. Alteração em contratos existentes por tela de edição planejada (BL-032). | Implementado (edição planejada) |
| RF02.2 | Vínculo de bens e veículos | Associar bens, chassis e carrocerias a um contrato. | Planejado para a versão 1.0 |
| RF03 | Consulta de contratos | Exibir contratos cadastrados para consulta operacional. | Implementado |
| RF03.1 | Filtros de contratos | Filtrar contratos por empresa e banco (seleção entre os cadastros, com a opção Todos), número (busca parcial) e por "Somente sem anexos" (sem anexo de contrato ou de ficha financeira). Filtros adicionais (taxa, período, valor, tipo) planejados para evolução. | Parcialmente implementado |
| RF03.2 | Detalhe e anexos do contrato | Botão Detalhes em Contratos abre o detalhe em abas (Dados, Contrato, Ficha Financeira, Histórico); anexar vários PDFs de contrato e de ficha financeira (até 20 MB cada) — também já na inclusão do contrato, na mesma transação —, visualizá-los na tela, baixar e excluir; colunas Anexo contrato / Anexo ficha na lista. Ver UC14. | Implementado |
| RF04 | Consulta de veículos | Exibir bens e veículos associados aos contratos. | Planejado para a versão 1.0 |
| RF04.1 | Filtros de veículos | Filtrar veículos por banco, taxa, período, valor e situação. | Planejado |
| RF05 | Exclusão física de contratos | Remover fisicamente um contrato mediante confirmação e respeitando integridade referencial; contrato com liquidação, antecipação ou quitação não pode ser excluído e a tela informa o motivo. | Implementado, sujeito a dependências |
| RF06 | Exclusão de veículos | Remover bens ou veículos conforme regras de integridade. | Planejado |
| RF07 | Projeção financeira | Exibir parcelas e valores calculados pelo PostgreSQL e gravados em `projecao_parcelas`, recalculados automaticamente por contrato (DA08). | Implementado |
| RF07.1 | Quitação/Antecipação de contrato | Registrar, em um único fluxo (botão Quitação/Antecipação em Contratos), a antecipação (pagamento parcial) ou a quitação total de um contrato, calculando saldo devedor e Selic da data informada antes da confirmação; excluir um lançamento pela tela Antecipação; a projeção do contrato é recalculada em ambos os casos. | Implementado para contratos BNDES FINAME SELIC |
| RF07.2 | Liquidação de parcelas | Em Operacional > Liquidação, listar as parcelas (filtros por empresa, banco, contrato, vencimento e situação; padrão no mês atual), liquidar manualmente uma ou mais parcelas abertas informando data e valor pago (diferença gravada como ajuste) e estornar liquidações com motivo. Ver UC07. | Implementado |
| RF07.3 | Relatório Contas a Pagar | Exibir, em Relatórios > Contas a Pagar, a posição na data base (RN24) de todas as parcelas, antecipações e quitações, com valor projetado, valor pago, ajuste e valor considerado; filtros por data base (hoje), empresa, banco, contrato, vencimento (mês atual) e situação; resumo por situação e exportação para Excel (CSV se o ambiente não tiver `openpyxl`). | Implementado |
| RF07.4 | Relatório de endividamento | Exibir, em Relatórios > Endividamento, o endividamento na posição da data base agrupado por ano, mês e modalidade (fluxo de caixa, R$ milhões): Financiamentos (RN24, contratos contabilizados até a data base, RN28), Compra Santo Anjo, Consórcios e Tributário (RN29); filtros por data base (hoje) e vencimentos a partir do mês (01/01/2026); Saldo Acumulado, blocos por ano, meses com parcelas liquidadas destacados, bloco Sub Total com total pago e total a pagar por modalidade, créditos de consórcio e Dívida Líquida; tema claro/escuro; botão **Gerar PDF** (impressão do navegador, A4 paisagem, tema claro, sem o resumo do mês). Totais e resumo somam o valor exato e arredondam só o resultado. | Implementado (em calibração) |
| RF07.4.1 | Resumo do mês do endividamento | Exibir, abaixo do relatório de endividamento, a variação do mês por modalidade (Saldo Inicial, Juros, Pgto Mês, Contrato Quitado, Contrato Novo, Saldo Final), com total, créditos de consórcio e Dívida Líquida (RN30). | Implementado (em calibração) |
| RF07.5 | Consulta de antecipações | Exibir, em Operacional > Antecipação, todas as antecipações e quitações registradas (id, empresa, banco, contrato, data de pagamento, valor pago e tipo de lançamento), com filtros por Empresa e Banco (seleção entre os cadastros, com a opção Todos), Contrato (busca parcial) e intervalo de Data de Pagamento (padrão: mês atual) aplicados no banco, e resumo abaixo da tabela (quantidade de empresas, bancos e contratos e total pago). | Implementado |
| RF07.6 | Conciliação com o ERP | Em Liquidação > Importar ERP, importar o CSV de pagamentos do ERP para os contratos marcados (ou todos os filtrados), mostrar a prévia por chave (RN22) com as situações Conciliado, Diferença, Vínculo conflitante, Não identificado no Nexus, Não pago no ERP, Já liquidada e Fora da seleção, e liquidar as linhas marcadas gravando a diferença como ajuste. O relatório do ERP não é guardado (DA09). Ver UC13. | Implementado |
| RF07.7 | Vínculo ERP → Nexus | Na prévia da conciliação, vincular códigos do ERP não identificados a um ou mais contratos do Nexus (lista montada e gravada de uma vez), de forma permanente, e remover vínculos. | Implementado (tela de cadastro planejada) |
| RF07.8 | Painel de indicadores | Exibir, em Painel > Indicadores, na posição da data base (RN24) e sempre comparando dois anos, Data X × Data Y (RN27): saldo devedor, fluxo de pagamentos, juros no período, contratado no período e taxa média ponderada; gráfico do fluxo de pagamentos por mês (X × Y) e composição do fluxo por empresa, banco ou tipo de contrato; filtros por ano: Data base (padrão ano atual), Data X (padrão ano anterior) e Data Y (padrão ano atual), e empresa e banco. Contratos considerados a partir da data de contabilização (RN28). Ver UC15. | Implementado (em calibração) |
| RF07.9 | Consórcio | Em Operacional > Consórcio, importar por banco e consorciado o CSV de pagamentos (pago) e o CSV de parcelas a pagar das cotas contempladas (foto por competência), lançar os créditos de consórcio do fechamento do mês e consultar pago, a pagar e créditos com filtros. Ver UC16. | Implementado |
| RF07.10 | Outros pagamentos | Em Operacional > Outros Pagamentos, lançar parcelas de Compra Santo Anjo e Tributário (uma ou várias parcelas mensais), editar e excluir parcelas em aberto, dar baixa (data e valor pago) e estornar a baixa, com filtros por modalidade, vencimento e situação e resumo. Ver UC17. | Implementado |
| RF08 | Detalhamento e auditoria | Exibir detalhes do registro e histórico de alterações. | Parcialmente implementado |
| RF08.1 | Log de auditoria | Registrar em `financiamento.log_auditoria` cada operação de escrita (inclusão e exclusão de contrato, quitação/antecipação e sua exclusão, liquidação e estorno, conciliação com o ERP, vínculos ERP, importação da Selic, inclusão e exclusão de anexos, importação de consórcio e créditos, inclusão/alteração/exclusão/baixa/estorno de outros pagamentos, cadastro de senha) e cada evento de acesso (login, falha de login, logout, sessão encerrada), com usuário, data/hora, ação, registro afetado, resultado, detalhes e IP. O log de uma escrita é gravado na mesma transação da operação; falhas também são registradas. O log é somente inserção. | Implementado |
| RF08.2 | Consulta do histórico | Exibir na interface o histórico de operações de um registro e do sistema, a partir do log de auditoria. | Planejado |
| RF09 | Ajustes financeiros | Registrar a diferença entre o valor pago e o projetado de cada parcela como ajuste da liquidação, sem alterar o saldo devedor (RN20). | Implementado (via liquidação) |
| RF10 | Autenticação e perfis | Controlar acesso por usuário e perfil. | Parcialmente implementado (autenticação implementada; perfis planejados) |
| RF10.1 | Login | Exigir usuário e senha antes de exibir qualquer tela do sistema; credenciais validadas no cadastro único do Sistema Nexus (`nexus.usuarios`), exigindo acesso ao módulo em `nexus.usuario_modulos` (`financiamento`); usuários e acessos administrados pelo portal. Erros exibem notificação genérica ("Usuário ou senha incorretos."), sem revelar se o usuário existe. Botão **Sair** na barra lateral encerra a sessão e recarrega a página. | Implementado |
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
