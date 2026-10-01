SELECT_USUARIO = '''
	SELECT id, usuario, senha_hash, ativo
	FROM financiamento.usuarios
	WHERE usuario = :usuario
'''

CADASTRAR_SENHA = '''
	UPDATE financiamento.usuarios
	SET senha_hash = :senha_hash,
		senha_definida_em = now()
	WHERE id = :id
	AND senha_hash IS NULL
	AND ativo
'''
