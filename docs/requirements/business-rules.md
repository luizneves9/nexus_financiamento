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
| RN11 | Autorização | Autenticação, perfis e autorizações formais seráo implementados na versão 1.0. | Planejada |
| RN12 | Auditoria | Historico de inclusões, alterações e exclusões será avaliado em evolução futura. | Planejada |
| RN13 | Quitação única por contrato | Um contrato não pode ter mais de um lançamento do tipo QUITACAO; o sistema bloqueia o registro de uma nova quitação quando já existe uma para o contrato. | Atual |
| RN14 | Ordem das datas de antecipação/liquidação | Na tela de Antecipação/Liquidação, a data de compensação deve ser maior ou igual à data de tesouraria, que deve ser maior ou igual à data de pagamento. | Atual |
| RN15 | Escopo de cálculo por modalidade | O cálculo de saldo devedor e Selic exibido na tela de Antecipação/Liquidação antes da confirmação usa `mv_projecao_moeda`, que só contém projeção para contratos do tipo BNDES FINAME SELIC. Demais modalidades não são suportadas nesta versão. | Atual, limitação conhecida |

## Regras ainda não formalizadas

- Unicidade de chassi e placa.
- Comportamento de bens duplicados em contratos ativos.
- Politica para Selic ausente em uma data de cálculo.
- Atualização das matérialized views apos cada tipo de operação (formalizada para inclusão de contrato e para antecipação/quitação; demais operações, como exclusão, ainda não cobertas por trigger).
- Regras de ajuste apos vencimento.
- Retencao e aprovação de histórico.
