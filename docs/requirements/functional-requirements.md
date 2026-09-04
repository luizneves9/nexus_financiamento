# Requisitos Funcionais (RF)

Este documento especifica as funcionalidades necessárias para o sistema de Gestão de Financiamentos do Grupo GBS.

| ID | Nome | Descrição | 
| :--- | :--- | :--- | 
| **RF01** | Importação da Selic | O sistema deve obter/importar automaticamente os dados atualizados da taxa Selic via integração/job. | 
| **RF02** | Inclusão Manual de Contratos | Permitir o cadastro manual de contratos atrelados a um ou mais veículos. | 
| **RF02.1**| Interface Web de Contrato | Fornecer formulário web com validação para inclusão de contratos. | 
| **RF02.2**| Alienação de Veículos | Permitir a inclusão/vínculo dos veículos (Chassi/Carroceria) que serão alienados ao contrato. | 
| **RF03** | Listagem de Contratos | Exibir a lista completa dos contratos cadastrados no sistema. | 
| **RF03.1**| Filtros de Contrato | Permitir filtrar contratos por banco, taxa, período de emissão, valor e tipo de contrato. | 
| **RF04** | Listagem de Veículos | Exibir a lista de veículos alienados associados aos contratos. | 
| **RF04.1**| Filtros de Veículos | Permitir filtragem de veículos por banco financiado, taxa, período, valor e situação. | 
| **RF05** | Exclusão de Contratos | Permitir a exclusão lógica/física de contratos (respeitando travas de integridade). | 
| **RF06** | Exclusão de Veículos | Permitir a remoção de veículos cadastrados da base. | 
| **RF07** | Liquidação e Simulação | Permitir simulação de quitação (total ou parcial) considerando contrato, valor presente e veículos. | 
| **RF08** | Detalhamento / Audit Trail | Exibir o histórico de auditoria e fluxo de vida do dado (inclusões, pagamentos, alterações). | 
| **RF09** | Manutenção e Aprovação | Após a data de vencimento, permitir ao usuário incluir ajustes financeiros e aprovar o pagamento. | 