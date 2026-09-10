SELECT_PROJECAO = '''
	WITH selic AS (
		SELECT valor
		FROM financiamento.selic
		ORDER BY data DESC
		LIMIT 1
	),
	valores_moeda AS (
		SELECT
			parcela AS "Parcela",
			data_vcto AS "Data de Vencimento",
			ROUND(COALESCE(valor_pagamento, total_parcela * s.valor), 2) AS "Valor"
		FROM financiamento.mv_projecao_moeda_final
		CROSS JOIN selic s
		WHERE id_contrato = :id
	),
	valores_tfc AS (
		SELECT 
			parcela AS "Parcela",
			data_vcto AS "Data de Vencimento",
			total_parcela AS "Valor"
		FROM financiamento.mv_projecao_tfc
		WHERE id_contrato = :id
	)
	SELECT "Parcela", "Data de Vencimento", "Valor" FROM valores_moeda
	UNION ALL
	SELECT "Parcela", "Data de Vencimento", "Valor" FROM valores_tfc
'''

DELETE_CONTRATO = '''
	DELETE FROM financiamento.contratos
	WHERE id = :id
'''