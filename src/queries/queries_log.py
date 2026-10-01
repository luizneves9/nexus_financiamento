INSERIR_LOG = '''
	INSERT INTO financiamento.log_auditoria (
		id_usuario,
		usuario,
		acao,
		entidade,
		id_registro,
		sucesso,
		detalhes,
		ip
	) VALUES (
		:id_usuario,
		:usuario,
		:acao,
		:entidade,
		:id_registro,
		:sucesso,
		CAST(:detalhes AS jsonb),
		:ip
	)
'''
