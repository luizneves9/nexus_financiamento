from queries.queries_contas_a_pagar import CTE_POSICAO_DATA_BASE

# Endividamento na posição da data base (mesma regra do Contas a Pagar): soma do valor considerado
# por ano/mês do vencimento útil, em milhões, separando o pago (até a data base) do a pagar (projetado);
# o mês é marcado como pago/parcial só por parcelas liquidadas (antecipações e quitações não marcam);
# filtros opcionais de data de corte (vencimento a partir de), empresa e banco.
SELECT_PROJECAO_ENDIVIDAMENTO = CTE_POSICAO_DATA_BASE + '''
	SELECT
		EXTRACT(YEAR FROM vencimento_util)::int AS ano,
		EXTRACT(MONTH FROM vencimento_util)::int AS mes,
		'Financiamento' AS categoria,
		ROUND(SUM(valor_considerado) / 1000000, 3) AS valor,
		ROUND(SUM(CASE WHEN situacao <> 'Projetado' THEN valor_considerado ELSE 0 END) / 1000000, 3) AS valor_pago,
		ROUND(SUM(CASE WHEN situacao = 'Projetado' THEN valor_considerado ELSE 0 END) / 1000000, 3) AS valor_a_pagar,
		bool_or(situacao = 'Liquidado') AND NOT bool_or(situacao = 'Projetado') AS mes_pago,   -- só parcelas liquidadas
		bool_or(situacao = 'Liquidado') AS mes_com_pagamento                                  -- antecipação/quitação não marcam
	FROM posicao
	WHERE (CAST(:data_corte AS date) IS NULL OR vencimento_util >= date_trunc('month', CAST(:data_corte AS date))::date)   -- a partir do mês da data de corte
	AND (:empresa IS NULL OR nome_empresa ILIKE :empresa)
	AND (:banco IS NULL OR banco ILIKE :banco)
	GROUP BY 1, 2
	ORDER BY 1, 2
'''
