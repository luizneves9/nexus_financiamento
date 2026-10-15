SELECT_PROJECAO_ENDIVIDAMENTO = '''
    WITH valor_endividamento AS (
        SELECT
            EXTRACT(YEAR from data_vcto) AS ano,
            EXTRACT(MONTH from data_vcto) AS mes,
            'Financiamento' AS categoria,
            ROUND(SUM(total_parcela) / 1000000, 3) AS valor
        FROM financiamento.vw_agrupamento_projecao
        GROUP BY EXTRACT(YEAR from data_vcto), EXTRACT(MONTH from data_vcto)
        )
        SELECT
            ano,
            mes,
            categoria,
            SUM(valor) AS valor
        FROM valor_endividamento
        GROUP BY ano, mes, categoria
        ORDER BY ano, mes, categoria
'''
