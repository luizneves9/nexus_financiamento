# Regras de Negócio (RN)

Este documento lista as restrições, políticas e regras operacionais impostas ao sistema.

### [RN01] Anti-Duplicidade
* **Descrição:** O sistema deve impedir a inserção de contratos ou veículos duplicados.
* **Critério de Aceite:** 
  * Não deve ser permitido cadastrar dois contratos com o mesmo `numero_contrato` para o mesmo `id_banco`.
  * Não deve ser permitido cadastrar veículos com o mesmo `chassi` ou `placa` em contratos ativos.

### [RN02] Projeção Financeira
* **Descrição:** A projeção do saldo devedor e parcelas deve utilizar a taxa Selic acumulada diária sobre dias úteis, considerando a tabela de feriados bancários cadastrada.

### [RN03] Pós-Vencimento e Aprovação
* **Descrição:** Ações de ajustes e baixas definitivas para parcelas após a data de vencimento exigem confirmação explícita/aprovação do usuário do setor financeiro.