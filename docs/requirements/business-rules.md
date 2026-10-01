# Regras de Negócio

Estas regras representam as políticas do domínio de financiamentos e o
comportamento atualmente definido para o projeto.

| ID | Regra | Descricao | Status |
| --- | --- | --- | --- |
| RN01 | Unicidade de contrato | O número do contrato deve obedecer a restrição de unicidade atualmente definida no banco. Regras específicas por banco seráo avaliadas posteriormente. | Atual |
| RN02 | Projeção no banco | Saldos, parcelas, juros e antecipações são calculados exclusivamente pelo PostgreSQL. | Atual |
| RN02.1 | Projeção temporária | A projeção solicitada durante a inclusão deve ser calculada por função PostgreSQL parametrizada, sem persistir o contrato ou alterar dados permanentes. | Atual |
| RN03 | Dias úteis | Finais de semana e datas cadastradas em `financiamento.feriados` não são considerados dias úteis. | Atual |
| RN04 | Selic do contrato | A Selic do contrato e obtida pela última taxa disponível até a data BNDES. | Atual |
| RN05 | Selic da antecipação | A Selic da antecipação e obtida pela última taxa disponível até a data de tesouraria. | Atual |
| RN06 | Carência | Contratos seguem a regra inicial de possuir período de carência. O pagamento durante a carência pode ser zero, mas nunca negativo. | Atual |
| RN07 | Exclusão inicial | Contratos são excluídos físicamente mediante confirmação do usuário. | Atual |
| RN08 | Integridade referencial | Contratos, bens, antecipações, empresas, bancos e fornecedores respeitam as chaves estrangeiras do banco. | Atual |
| RN09 | Antecipação efetiva | Antecipação deve ser registrada pela tela de Antecipação/Liquidação, e não apenas simulada. | Atual |
| RN10 | Liquidação | A quitação total do contrato é registrada como um lançamento de antecipação com `tipo_lancamento = QUITACAO`, sem estrutura de dados própria. | Atual |
| RN11 | Autorização | O acesso exige autenticação (RN16 a RN18). Perfis e autorizações por aba/ação seráo implementados na versão 1.0. | Parcial (autenticação atual; perfis planejados) |
| RN12 | Auditoria | Toda operação de escrita e todo evento de acesso são registrados em `financiamento.log_auditoria`. O log de uma escrita é gravado na mesma transação da operação (sem log, sem operação); falhas são registradas com `sucesso = false`. O log é somente inserção e nunca contém senha, hash ou token. Consultas somente leitura não são registradas. | Atual |
| RN13 | Quitação única por contrato | Um contrato não pode ter mais de um lançamento do tipo QUITACAO; o sistema bloqueia o registro de uma nova quitação quando já existe uma para o contrato. | Atual |
| RN14 | Ordem das datas de antecipação/liquidação | Na tela de Antecipação/Liquidação, a data de compensação deve ser maior ou igual à data de tesouraria, que deve ser maior ou igual à data de pagamento. | Atual |
| RN15 | Escopo de cálculo por modalidade | O cálculo de saldo devedor e Selic exibido na tela de Antecipação/Liquidação antes da confirmação usa `mv_projecao_moeda`, que só contém projeção para contratos do tipo BNDES FINAME SELIC. Demais modalidades não são suportadas nesta versão. | Atual, limitação conhecida |
| RN16 | Criação de usuários | Usuários são criados somente pelo desenvolvedor, diretamente no banco, sem senha. No primeiro acesso o usuário entra com a senha vazia e cadastra a própria senha. Reset de senha = voltar `senha_hash` para nulo; bloqueio = `ativo = false`. | Atual |
| RN17 | Senha | A senha deve ter no mínimo 8 caracteres, ser confirmada no cadastro e é armazenada somente como hash `scrypt` com salt aleatório por usuário; ninguém (nem o desenvolvedor) consegue ler a senha. | Atual |
| RN18 | Sessão | O login permanece válido por 30 minutos após o último uso (cookie assinado), inclusive após fechar o navegador. **Sair** encerra a sessão imediatamente. Usuário bloqueado ou com senha resetada perde o acesso no próximo login ou em até 5 minutos se estiver com a sessão aberta. | Atual |

## Regras ainda não formalizadas

- Unicidade de chassi e placa.
- Comportamento de bens duplicados em contratos ativos.
- Politica para Selic ausente em uma data de cálculo.
- Atualização das matérialized views apos cada tipo de operação (formalizada para inclusão de contrato e para antecipação/quitação; demais operações, como exclusão, ainda não cobertas por trigger).
- Regras de ajuste apos vencimento.
- Retenção e expurgo do log de auditoria (hoje o log é mantido indefinidamente).
- Limite de tentativas de login e bloqueio temporário (ver BL-016).
