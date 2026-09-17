SELECT_PROJECAO_ENDIVIDAMENTO = '''
    SELECT
        EXTRACT(YEAR from data_vcto) AS ano,
        EXTRACT(MONTH from data_vcto) AS mes,
        'Financiamento' AS categoria,
        ROUND(SUM(total_parcela) / 1000000, 3) AS valor
    FROM financiamento.vw_agrupamento_projecao
    GROUP BY EXTRACT(YEAR from data_vcto), EXTRACT(MONTH from data_vcto)
    ORDER BY EXTRACT(YEAR from data_vcto), EXTRACT(MONTH from data_vcto)
'''
