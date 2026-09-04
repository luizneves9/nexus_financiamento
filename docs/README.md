# Nexus  -  Gestão de Financiamentos

> **Versão:** 1.0 (Em fase de desenvolvimento)  
> **Domínio:** Gestão e controle de contratos de financiamentos e ativos (veículos) do Grupo GBS.

## Visão Geral

O **Nexus - Gestão de Financiamentos** é uma plataforma voltada para a gestão centralizada, controle de financiamentos de veículos e simulação de liquidação. O sistema automatiza o cálculo de juros (com base na Selic), projeção de amortização/parcelas e acompanhamento de baixas e pagamentos.

---

## Mapeamento Macro do Processo

```mermaid
graph TD
    A[Entrada: Inclusão Manual do Contrato + Anexos] --> B[Processamento: Preenchimento da Tabela de Controle]
    B --> C[Processamento: Atribuição de Bens/Veículos]
    C --> D[Processamento: Projeção de Parcelas a Pagar]
    D --> E[Saída: Painel de Gestão e Relatórios]
    D --> F[Saída: Simulação de Liquidação e Evolução]
