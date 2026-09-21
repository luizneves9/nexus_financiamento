# UC07 - Liquidação de Contrato (consolidado em UC06)

**Status:** Consolidado em UC06
**Requisitos associados:** RF07.2 (consolidado em RF07.1)

Este Use Case foi consolidado em
[UC06 - Antecipação e Liquidação Antecipada de Contrato](UC06-registro-de-antecipacao.md).

A liquidação total de um contrato não tem mais um fluxo ou estrutura de
dados próprios: ela é registrada no mesmo modal de antecipação, selecionando
o tipo de lançamento `QUITACAO`, e persistida em
`financiamento.antecipacao` como qualquer outro lançamento. Consulte UC06
para o objetivo, o fluxo completo, os fluxos de exceção e as regras de
negócio atualizados.

Este arquivo é mantido como registro histórico e para preservar referências
existentes na documentação (Matriz de Rastreabilidade, Registro de Status e
Pendências).
