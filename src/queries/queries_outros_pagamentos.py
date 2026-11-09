# Outros pagamentos do Endividamento (Compra Santo Anjo e Tributário): parcelas lançadas manualmente,
# com baixa (data e valor pago) e estorno que limpa a baixa (database/consorcio_outros_pagamentos.sql).

COLUNAS_OUTROS_PAGAMENTOS = '''
	id, modalidade, descricao, data_vencimento, valor,
	CASE WHEN data_pagamento IS NULL THEN 'ABERTA' ELSE 'PAGA' END AS situacao,
	data_pagamento, valor_pago, usuario, data_registro, usuario_alteracao, data_alteracao, usuario_baixa, data_registro_baixa
'''

SELECT_OUTROS_PAGAMENTOS = f'''
	SELECT {COLUNAS_OUTROS_PAGAMENTOS}
	FROM financiamento.outros_pagamentos
	WHERE (:modalidade IS NULL OR modalidade = :modalidade)
	AND (CAST(:data_vcto_ini AS date) IS NULL OR data_vencimento >= :data_vcto_ini)
	AND (CAST(:data_vcto_fim AS date) IS NULL OR data_vencimento <= :data_vcto_fim)
	AND (:situacao IS NULL
		OR (:situacao = 'ABERTA' AND data_pagamento IS NULL)
		OR (:situacao = 'PAGA' AND data_pagamento IS NOT NULL))
	ORDER BY data_vencimento, modalidade, id
'''

SELECT_OUTROS_PAGAMENTOS_POR_ID = f'''
	SELECT {COLUNAS_OUTROS_PAGAMENTOS}
	FROM financiamento.outros_pagamentos
	WHERE id = ANY(:ids)
	ORDER BY data_vencimento, id
'''

# parcela já paga na inclusão grava também quem e quando registrou a baixa
INSERIR_OUTRO_PAGAMENTO = '''
	INSERT INTO financiamento.outros_pagamentos (
		modalidade, descricao, data_vencimento, valor, data_pagamento, valor_pago, usuario, usuario_baixa, data_registro_baixa)
	VALUES (
		:modalidade, :descricao, :data_vencimento, :valor, :data_pagamento, :valor_pago, :usuario,
		CASE WHEN CAST(:data_pagamento AS date) IS NOT NULL THEN :usuario END,
		CASE WHEN CAST(:data_pagamento AS date) IS NOT NULL THEN now() END)
	RETURNING id
'''

# só parcela em aberto pode ser alterada, baixada ou excluída (o WHERE garante, mesmo com a tela desatualizada)
ALTERAR_OUTRO_PAGAMENTO = '''
	UPDATE financiamento.outros_pagamentos
	SET modalidade = :modalidade,
		descricao = :descricao,
		data_vencimento = :data_vencimento,
		valor = :valor,
		usuario_alteracao = :usuario,
		data_alteracao = now()
	WHERE id = :id
	AND data_pagamento IS NULL
	RETURNING id
'''

BAIXAR_OUTRO_PAGAMENTO = '''
	UPDATE financiamento.outros_pagamentos
	SET data_pagamento = :data_pagamento,
		valor_pago = :valor_pago,
		usuario_baixa = :usuario,
		data_registro_baixa = now()
	WHERE id = :id
	AND data_pagamento IS NULL
	RETURNING id
'''

# estorno: limpa a baixa e devolve a baixa estornada (para o log)
ESTORNAR_OUTRO_PAGAMENTO = '''
	WITH antes AS (
		SELECT id, data_pagamento, valor_pago, usuario_baixa, data_registro_baixa
		FROM financiamento.outros_pagamentos
		WHERE id = :id
		AND data_pagamento IS NOT NULL
		FOR UPDATE
	)
	UPDATE financiamento.outros_pagamentos o
	SET data_pagamento = NULL,
		valor_pago = NULL,
		usuario_baixa = NULL,
		data_registro_baixa = NULL,
		usuario_alteracao = :usuario,
		data_alteracao = now()
	FROM antes
	WHERE o.id = antes.id
	RETURNING o.id, o.modalidade, o.descricao, o.data_vencimento, o.valor,
		antes.data_pagamento, antes.valor_pago, antes.usuario_baixa, antes.data_registro_baixa
'''

EXCLUIR_OUTRO_PAGAMENTO = '''
	DELETE FROM financiamento.outros_pagamentos
	WHERE id = :id
	AND data_pagamento IS NULL
	RETURNING *
'''
