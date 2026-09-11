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

PROJETAR_CONTRATO_SELIC = '''
	SELECT *
	FROM financiamento.projetar_contrato_selic(
		:data_emissao,
		:data_bndes,
		:valor_financiado,
		:taxa_juros_efetiva,
		:prazo_carencia,
		:prazo_final,
		:carencia_pagamento,
		:registro_cobranca
	)
	ORDER BY parcela
'''

PROJETAR_CONTRATO_TFC = '''
	SELECT *
	FROM financiamento.projetar_contrato_tfc(
		:data_emissao,
		:data_bndes,
		:valor_financiado,
		:taxa_juros_efetiva,
		:prazo_carencia,
		:prazo_final,
		:carencia_pagamento
	)
	ORDER BY parcela
'''

DELETE_CONTRATO = '''
	DELETE FROM financiamento.contratos
	WHERE id = :id
'''