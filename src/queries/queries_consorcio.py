# Consórcio: pagamentos (histórico pela data de pagamento, um arquivo por banco + consorciado), parcelas a pagar
# (foto por data base/competência, banco e consorciado) e créditos do fechamento do mês (database/consorcio_outros_pagamentos.sql).

# ---------------------------------------------------------------------
# Pago
# ---------------------------------------------------------------------
SELECT_CONSORCIO_PAGO = '''
	SELECT id, banco, nome_consorciado, numero_proposta, id_cota, data_adesao, movimento, data_pagamento,
		valor_fundo_comum, valor_fundo_reserva, valor_taxa_administracao, valor_multa_juros, valor_outros, valor_total,
		nome_arquivo, usuario, data_registro
	FROM financiamento.consorcio_pago
	WHERE (CAST(:data_ini AS date) IS NULL OR data_pagamento >= :data_ini)
	AND (CAST(:data_fim AS date) IS NULL OR data_pagamento <= :data_fim)
	AND (:banco IS NULL OR banco ILIKE :banco)
	AND (:consorciado IS NULL OR nome_consorciado ILIKE :consorciado)
	AND (:proposta IS NULL OR numero_proposta ILIKE :proposta)
	ORDER BY data_pagamento, banco, nome_consorciado, numero_proposta, id
'''

# o que será substituído na reimportação: pagamentos do banco + consorciado no período coberto pelo arquivo
SELECT_RESUMO_PAGO_PERIODO = '''
	SELECT count(*) AS qtd, COALESCE(sum(valor_total), 0) AS total
	FROM financiamento.consorcio_pago
	WHERE banco = :banco
	AND nome_consorciado = :nome_consorciado
	AND data_pagamento BETWEEN :data_ini AND :data_fim
'''

EXCLUIR_PAGO_PERIODO = '''
	DELETE FROM financiamento.consorcio_pago
	WHERE banco = :banco
	AND nome_consorciado = :nome_consorciado
	AND data_pagamento BETWEEN :data_ini AND :data_fim
'''

INSERIR_CONSORCIO_PAGO = '''
	INSERT INTO financiamento.consorcio_pago (
		competencia, banco, nome_consorciado, numero_proposta, data_adesao, id_cota, movimento, data_pagamento,
		valor_fundo_comum, valor_fundo_reserva, valor_taxa_administracao, valor_multa_juros, valor_outros, valor_total,
		nome_arquivo, usuario)
	VALUES (
		:competencia, :banco, :nome_consorciado, :numero_proposta, :data_adesao, :id_cota, :movimento, :data_pagamento,
		:valor_fundo_comum, :valor_fundo_reserva, :valor_taxa_administracao, :valor_multa_juros, :valor_outros, :valor_total,
		:nome_arquivo, :usuario)
'''

# ---------------------------------------------------------------------
# A pagar
# ---------------------------------------------------------------------
SELECT_CONSORCIO_A_PAGAR = '''
	SELECT id, competencia, banco, nome_consorciado, numero_proposta, data_pagamento, valor_parcela, data_emissao,
		nome_arquivo, usuario, data_registro
	FROM financiamento.consorcio_a_pagar
	WHERE competencia = :competencia
	AND (:banco IS NULL OR banco ILIKE :banco)
	AND (:consorciado IS NULL OR nome_consorciado ILIKE :consorciado)
	AND (:proposta IS NULL OR numero_proposta ILIKE :proposta)
	ORDER BY banco, nome_consorciado, data_pagamento, numero_proposta, id
'''

# o que será substituído na reimportação: a foto daquela competência para o banco + consorciado do arquivo
SELECT_RESUMO_A_PAGAR_COMPETENCIA = '''
	SELECT count(*) AS qtd, COALESCE(sum(valor_parcela), 0) AS total
	FROM financiamento.consorcio_a_pagar
	WHERE competencia = :competencia
	AND banco = :banco
	AND nome_consorciado = :nome_consorciado
'''

EXCLUIR_A_PAGAR_COMPETENCIA = '''
	DELETE FROM financiamento.consorcio_a_pagar
	WHERE competencia = :competencia
	AND banco = :banco
	AND nome_consorciado = :nome_consorciado
'''

INSERIR_CONSORCIO_A_PAGAR = '''
	INSERT INTO financiamento.consorcio_a_pagar (
		competencia, banco, nome_consorciado, numero_proposta, valor_parcela, data_pagamento, data_emissao, nome_arquivo, usuario)
	VALUES (
		:competencia, :banco, :nome_consorciado, :numero_proposta, :valor_parcela, :data_pagamento, :data_emissao, :nome_arquivo, :usuario)
'''

# consorciados já importados (lista do campo Consorciado na importação do a pagar)
SELECT_CONSORCIADOS = '''
	SELECT nome_consorciado FROM financiamento.consorcio_pago WHERE nome_consorciado IS NOT NULL
	UNION
	SELECT nome_consorciado FROM financiamento.consorcio_a_pagar
	ORDER BY 1
'''

# ---------------------------------------------------------------------
# Créditos do fechamento do mês
# ---------------------------------------------------------------------
SELECT_CONSORCIO_CREDITO = '''
	SELECT id, competencia, credito_cotas_contempladas, credito_parcelas_nao_contempladas,
		usuario, data_registro, data_alteracao
	FROM financiamento.consorcio_credito
	ORDER BY competencia DESC
'''

SELECT_CREDITO_COMPETENCIA = '''
	SELECT id, competencia, credito_cotas_contempladas, credito_parcelas_nao_contempladas
	FROM financiamento.consorcio_credito
	WHERE competencia = :competencia
'''

# inclui ou atualiza o lançamento da competência (um por mês)
SALVAR_CONSORCIO_CREDITO = '''
	INSERT INTO financiamento.consorcio_credito (competencia, credito_cotas_contempladas, credito_parcelas_nao_contempladas, usuario)
	VALUES (:competencia, :credito_cotas_contempladas, :credito_parcelas_nao_contempladas, :usuario)
	ON CONFLICT (competencia) DO UPDATE SET
		credito_cotas_contempladas = EXCLUDED.credito_cotas_contempladas,
		credito_parcelas_nao_contempladas = EXCLUDED.credito_parcelas_nao_contempladas,
		usuario = EXCLUDED.usuario,
		data_alteracao = now()
	RETURNING id
'''
