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
		SELECT p.id_contrato, p.parcela, p.data_vcto, p.saldo_devedor, 1 AS prioridade
		FROM financiamento.projecao_parcelas p
		INNER JOIN financiamento.contratos c ON c.id = p.id_contrato
		WHERE p.id_contrato = :id_contrato
		AND c.tipo_contrato = 'BNDES FINAME SELIC'
		AND p.situacao <> 'CANCELADA_QUITACAO'
		AND p.data_vcto >= :data_pagamento
		ORDER BY p.data_vcto ASC
		LIMIT 1
	)
	UNION ALL
	(
		SELECT p.id_contrato, p.parcela, p.data_vcto, p.saldo_devedor, 2 AS prioridade
		FROM financiamento.projecao_parcelas p
		INNER JOIN financiamento.contratos c ON c.id = p.id_contrato
		WHERE p.id_contrato = :id_contrato
		AND c.tipo_contrato = 'BNDES FINAME SELIC'
		AND p.situacao <> 'CANCELADA_QUITACAO'
		ORDER BY p.data_vcto DESC
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
	RETURNING id
'''

SELECT_ANTECIPACOES = '''
	SELECT
		a.id,
		e.razao_social AS nome_empresa,
		b.razao_social AS banco,
		c.numero_contrato,
		a.data_pagamento,
		a.valor_pago,
		a.tipo_lancamento
	FROM financiamento.antecipacao a
	INNER JOIN financiamento.contratos c ON a.id_contrato = c.id
	INNER JOIN financiamento.empresas e ON c.id_empresa = e.id
	INNER JOIN financiamento.bancos b ON c.id_banco = b.id
	WHERE (:empresa IS NULL OR e.razao_social ILIKE :empresa)
	AND (:banco IS NULL OR b.razao_social ILIKE :banco)
	AND (:contrato IS NULL OR c.numero_contrato ILIKE :contrato)
	AND (:data_pagamento_ini IS NULL OR a.data_pagamento >= :data_pagamento_ini)
	AND (:data_pagamento_fim IS NULL OR a.data_pagamento <= :data_pagamento_fim)
	ORDER BY a.id
'''

DELETE_ANTECIPACAO = '''
	DELETE FROM financiamento.antecipacao
	WHERE id = :id
	RETURNING *
'''
