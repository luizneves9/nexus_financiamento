SELECT_EMPRESAS = '''
    SELECT * FROM financiamento.empresas
'''

SELECT_BANCOS = '''
    SELECT * FROM financiamento.bancos
'''
INCLUIR_CONTRATO = '''
    INSERT INTO financiamento.contratos (id_empresa, id_banco, numero_contrato, data_emissao, data_bndes, tipo_contrato, valor_financiado, pos_fixado, custo_bndes, sobretaxa_bndes, percentual_banco, taxa_juros_efetiva, prazo_total, prazo_carencia, prazo_final, data_primeira_parcela_encargo, data_primeira_parcela_prestacao, data_ultima_parcela, debito_conta_corrente, carencia_pagamento)
    VALUES
        (:id_empresa, :id_banco, :contrato, :data_emissao, :data_bndes, :tipo, :valor, :pos_fixado, :custo_bndes, :sobretaxa_bndes, :juros_banco, :juros_total, :prazo_total, :prazo_carencia, :prazo_final, :data_primeira_parcela_encargo, :data_primeira_parcela_prestacao, :data_ultima_parcela, :debito_conta_corrente, :carencia_pagamento)
'''