SELECT_DADOS_CONTRATO = '''
	SELECT
		c.id,
		c.numero_contrato,
		e.razao_social AS empresa,
		b.razao_social AS banco,
		c.valor_financiado,
		c.data_emissao,
		c.data_ultima_parcela
	FROM financiamento.contratos c
	INNER JOIN financiamento.empresas e ON c.id_empresa = e.id
	INNER JOIN financiamento.bancos b ON c.id_banco = b.id
	WHERE c.id = :id_contrato
'''

SELECT_PARCELA_SALDO_DEVEDOR = '''
	(
		SELECT id_contrato, parcela, data_vcto, saldo_devedor, 1 AS prioridade
		FROM financiamento.mv_projecao_moeda
		WHERE id_contrato = :id_contrato
		AND data_vcto >= :data_pagamento
		ORDER BY data_vcto ASC
		LIMIT 1
	)
	UNION ALL
	(
		SELECT id_contrato, parcela, data_vcto, saldo_devedor, 2 AS prioridade
		FROM financiamento.mv_projecao_moeda
		WHERE id_contrato = :id_contrato
		ORDER BY data_vcto DESC
		LIMIT 1
	)
	ORDER BY prioridade
	LIMIT 1
'''

SELECT_SELIC = '''
	(
		SELECT valor, data, 1 AS prioridade
		FROM financiamento.selic
		WHERE data >= :data_pagamento
		ORDER BY data ASC
		LIMIT 1
	)
	UNION ALL
	(
		SELECT valor, data, 2 AS prioridade
		FROM financiamento.selic
		WHERE data IS NOT NULL
		ORDER BY data DESC
		LIMIT 1
	)
	ORDER BY prioridade
	LIMIT 1
'''

VERIFICAR_QUITACAO_EXISTENTE = '''
	SELECT COUNT(*) as count
	FROM financiamento.antecipacao
	WHERE id_contrato = :id_contrato
	AND tipo_lancamento = 'QUITACAO'
'''

INSERIR_ANTECIPACAO = '''
	INSERT INTO financiamento.antecipacao (
		id_contrato,
		data_pagamento,
		data_tesouraria,
		valor_pago,
		tipo_lancamento,
		data_compensacao
	) VALUES (
		:id_contrato,
		:data_pagamento,
		:data_tesouraria,
		:valor_pago,
		:tipo_lancamento,
		:data_compensacao
	)
'''
