SELECT_PROJECAO = '''
	WITH valores_parcelas AS (
		SELECT
			parcela::numeric AS "Parcela",
			'Parcela' AS "Tipo",
			data_vcto AS "Data de Vencimento",
			valor_pagamento AS "Valor"
		FROM financiamento.projecao_parcelas
		WHERE id_contrato = :id
		AND situacao <> 'CANCELADA_QUITACAO'
	),
	valores_antecipacao AS (
		SELECT
			0 AS "Parcela",
			INITCAP(tipo_lancamento) AS "Tipo",
			data_pagamento AS "Data de Vencimento",
			ROUND(valor_pago, 2) AS "Valor"
		FROM financiamento.antecipacao
		WHERE id_contrato = :id
	)
	SELECT "Parcela", "Tipo", "Data de Vencimento", "Valor" FROM valores_parcelas
	UNION ALL
	SELECT "Parcela", "Tipo", "Data de Vencimento", "Valor" FROM valores_antecipacao
	ORDER BY "Data de Vencimento"
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
	RETURNING *
'''

VERIFICAR_LIQUIDACAO_CONTRATO = '''
	SELECT count(*) AS qtd
	FROM financiamento.liquidacao
	WHERE id_contrato = :id
'''
