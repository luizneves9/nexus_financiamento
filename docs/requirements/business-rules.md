# Regras de Negócio

Estas regras representam as políticas do domínio de financiamentos e o
comportamento atualmente definido para o projeto.

| ID | Regra | Descricao | Status |
| --- | --- | --- | --- |
| RN01 | Unicidade de contrato | O número do contrato deve obedecer a restrição de unicidade atualmente definida no banco. Regras específicas por banco seráo avaliadas posteriormente. | Atual |
| RN02 | Projeção no banco | Saldos, parcelas, juros e antecipações são calculados exclusivamente pelo PostgreSQL e gravados em `projecao_parcelas`, recalculados por contrato a cada inclusão/alteração de contrato, antecipação/quitação ou Selic (DA08). | Atual |
| RN02.1 | Projeção temporária | A projeção solicitada durante a inclusão deve ser calculada por função PostgreSQL parametrizada, sem persistir o contrato ou alterar dados permanentes. | Atual |
| RN03 | Dias úteis | Finais de semana e datas cadastradas em `financiamento.feriados` não são considerados dias úteis. | Atual |
| RN04 | Selic do contrato | A Selic do contrato é obtida pela última taxa disponível até a data BNDES. A série vem do BNDES (RN25). | Atual |
| RN05 | Selic da antecipação | A Selic da antecipação e obtida pela última taxa disponível até a data de tesouraria. | Atual |
| RN06 | Carência | Contratos seguem a regra inicial de possuir período de carência. O pagamento durante a carência pode ser zero, mas nunca negativo. | Atual |
| RN07 | Exclusão inicial | Contratos são excluídos físicamente mediante confirmação do usuário. | Atual |
| RN08 | Integridade referencial | Contratos, bens, antecipações, empresas, bancos e fornecedores respeitam as chaves estrangeiras do banco. | Atual |
| RN09 | Antecipação efetiva | Antecipação deve ser registrada pela tela de Quitação/Antecipação, e não apenas simulada. A exclusão de um lançamento recalcula a projeção do contrato. | Atual |
| RN10 | Quitação | A quitação total do contrato é registrada como um lançamento de antecipação com `tipo_lancamento = QUITACAO`; as parcelas posteriores ficam como `CANCELADA_QUITACAO`. (A baixa de parcelas é a Liquidação, RN19.) | Atual |
| RN11 | Autorização | O acesso exige autenticação (RN16 a RN18). Perfis e autorizações por aba/ação seráo implementados na versão 1.0. | Parcial (autenticação atual; perfis planejados) |
| RN12 | Auditoria | Toda operação de escrita e todo evento de acesso são registrados em `financiamento.log_auditoria`. O log de uma escrita é gravado na mesma transação da operação (sem log, sem operação); falhas são registradas com `sucesso = false`. O log é somente inserção e nunca contém senha, hash ou token. Consultas somente leitura não são registradas. | Atual |
| RN13 | Quitação única por contrato | Um contrato não pode ter mais de um lançamento do tipo QUITACAO; o sistema bloqueia o registro de uma nova quitação quando já existe uma para o contrato. | Atual |
| RN14 | Ordem das datas de quitação/antecipação | Na tela de Quitação/Antecipação, a data de compensação deve ser maior ou igual à data de tesouraria, que deve ser maior ou igual à data de pagamento. | Atual |
| RN15 | Escopo de cálculo por modalidade | O cálculo de saldo devedor e Selic exibido na tela de Quitação/Antecipação antes da confirmação usa `projecao_parcelas` apenas para contratos do tipo BNDES FINAME SELIC. Demais modalidades não são suportadas nesta versão. | Atual, limitação conhecida |
| RN16 | Criação de usuários | Usuários são criados somente pelo desenvolvedor, diretamente no banco, sem senha. No primeiro acesso o usuário entra com a senha vazia e cadastra a própria senha. Reset de senha = voltar `senha_hash` para nulo; bloqueio = `ativo = false`. | Atual |
| RN17 | Senha | A senha deve ter no mínimo 8 caracteres, ser confirmada no cadastro e é armazenada somente como hash `scrypt` com salt aleatório por usuário; ninguém (nem o desenvolvedor) consegue ler a senha. | Atual |
| RN18 | Sessão | O login permanece válido por 30 minutos após o último uso (cookie assinado), inclusive após fechar o navegador. **Sair** encerra a sessão imediatamente. Usuário bloqueado ou com senha resetada perde o acesso no próximo login ou em até 5 minutos se estiver com a sessão aberta. | Atual |
| RN19 | Liquidação de parcela | Só parcelas ABERTAS podem ser liquidadas (manual ou por conciliação); a liquidação guarda o valor projetado do momento da baixa, e o recálculo nunca altera parcela liquidada. Uma quitação que cancelaria parcela liquidada é recusada. | Atual |
| RN20 | Ajuste | A diferença entre o valor pago e o projetado é gravada como ajuste na liquidação e não altera o saldo devedor. | Atual |
| RN21 | Estorno | Liquidação não pode ser alterada nem excluída: só estornada, com motivo; o estorno reabre a parcela e recalcula o contrato. Contrato com liquidação (inclusive estornada) não pode ser excluído. | Atual |
| RN22 | Chave da conciliação com o ERP | Docto do ERP antes do primeiro `-` + mês/ano do vencimento × número do contrato + mês/ano da data da parcela; linhas do ERP com a mesma chave são somadas (Valor Pago). Só o Valor Pago é comparado. | Atual |
| RN23 | Vínculo ERP → Nexus | Código do ERP diferente do número do contrato é resolvido por vínculo permanente; um código ligado a vários contratos forma um grupo (mesmo contrato dividido no Nexus), conciliado em conjunto e com o valor pago rateado proporcionalmente ao valor projetado (sobra de arredondamento na maior parcela). Parcela em dois grupos no mesmo mês = vínculo conflitante. | Atual |
| RN24 | Posição na data base | Nos relatórios, parcela liquidada até a data base vale o valor pago; as demais valem o projetado, refeito com a Selic conhecida até a data base; antecipações e quitações pagas depois da data base não entram, e o contrato é considerado como estava na data base. | Atual |
| RN25 | Importação da Selic | A Selic é importada da série oficial do BNDES (UM143), só com datas posteriores à última gravada. | Atual |

## Regras ainda não formalizadas

- Unicidade de chassi e placa.
- Comportamento de bens duplicados em contratos ativos.
- Politica para Selic ausente em uma data de cálculo.
- Tratamento de antecipações/quitações que venham no relatório do ERP (hoje ignoradas na conciliação).
- Retenção e expurgo do log de auditoria (hoje o log é mantido indefinidamente).
- Limite de tentativas de login e bloqueio temporário (ver BL-016).
