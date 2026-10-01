SELECT_PROJECAO_PAGAMENTOS = '''
    SELECT * FROM financiamento.vw_agrupamento_projecao
    WHERE (:empresa IS NULL OR nome_empresa ILIKE :empresa)
    AND (:banco IS NULL OR banco ILIKE :banco)
    AND (:contrato IS NULL OR numero_contrato ILIKE :contrato)
    AND (:data_vcto_ini IS NULL OR data_vcto >= :data_vcto_ini)
    AND (:data_vcto_fim IS NULL OR data_vcto <= :data_vcto_fim)
'''
