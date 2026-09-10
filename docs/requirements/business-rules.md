# Regras de Negocio

Estas regras representam as politicas do dominio de financiamentos e o
comportamento atualmente definido para o projeto.

| ID | Regra | Descricao | Status |
| --- | --- | --- | --- |
| RN01 | Unicidade de contrato | O numero do contrato deve obedecer a restricao de unicidade atualmente definida no banco. Regras especificas por banco serao avaliadas posteriormente. | Atual |
| RN02 | Projecao no banco | Saldos, parcelas, juros e antecipacoes sao calculados exclusivamente pelo PostgreSQL. | Atual |
| RN03 | Dias uteis | Finais de semana e datas cadastradas em `financiamento.feriados` nao sao considerados dias uteis. | Atual |
| RN04 | Selic do contrato | A Selic do contrato e obtida pela ultima taxa disponivel ate a data BNDES. | Atual |
| RN05 | Selic da antecipacao | A Selic da antecipacao e obtida pela ultima taxa disponivel ate a data de tesouraria. | Atual |
| RN06 | Carencia | Contratos seguem a regra inicial de possuir periodo de carencia. | Atual; validacoes adicionais futuras |
| RN07 | Exclusao inicial | Contratos sao excluidos fisicamente mediante confirmacao do usuario. | Atual |
| RN08 | Integridade referencial | Contratos, bens, antecipacoes, empresas, bancos e fornecedores respeitam as chaves estrangeiras do banco. | Atual |
| RN09 | Antecipacao efetiva | Antecipacao deve ser registrada, e nao apenas simulada. | Planejada na interface |
| RN10 | Liquidacao | Liquidacoes totais ou parciais devem ser registradas no banco. | Planejada |
| RN11 | Autorizacao | Autenticacao, perfis e autorizacoes formais serao implementados na versao 1.0. | Planejada |
| RN12 | Auditoria | Historico de inclusoes, alteracoes e exclusoes sera avaliado em evolucao futura. | Planejada |

## Regras ainda nao formalizadas

- Unicidade de chassi e placa.
- Comportamento de bens duplicados em contratos ativos.
- Politica para Selic ausente em uma data de calculo.
- Atualizacao das materialized views apos cada tipo de operacao.
- Regras de ajuste apos vencimento.
- Retencao e aprovacao de historico.
