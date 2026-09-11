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
| RN06 | Carencia | Contratos seguem a regra inicial de possuir período de carência. | Atual; validações adicionais futuras |
| RN07 | Exclusão inicial | Contratos são excluídos físicamente mediante confirmação do usuário. | Atual |
| RN08 | Integridade referencial | Contratos, bens, antecipações, empresas, bancos e fornecedores respeitam as chaves estrangeiras do banco. | Atual |
| RN09 | Antecipação efetiva | Antecipação deve ser registrada, e não apenas simulada. | Planejada na interface |
| RN10 | Liquidação | Liquidacoes totais ou parciais devem ser registradas no banco. | Planejada |
| RN11 | Autorização | Autenticação, perfis e autorizações formais seráo implementados na versão 1.0. | Planejada |
| RN12 | Auditoria | Historico de inclusões, alterações e exclusões será avaliado em evolução futura. | Planejada |

## Regras ainda não formalizadas

- Unicidade de chassi e placa.
- Comportamento de bens duplicados em contratos ativos.
- Politica para Selic ausente em uma data de cálculo.
- Atualização das matérialized views apos cada tipo de operação.
- Regras de ajuste apos vencimento.
- Retencao e aprovação de histórico.
