# Login pelo cadastro único do Sistema Nexus (schema nexus do banco fin, repositório nexus_portal):
# usuários em nexus.usuarios e acesso ao módulo em nexus.usuario_modulos (modulo = 'financiamento').
# permitido = false: usuário existe, mas sem permissão no Financiamento (o login é recusado).
SELECT_USUARIO = '''
	SELECT u.id, u.usuario, u.senha_hash, u.ativo,
		EXISTS (
			SELECT 1 FROM nexus.usuario_modulos um
			WHERE um.id_usuario = u.id AND um.modulo = 'financiamento'
		) AS permitido
	FROM nexus.usuarios u
	WHERE u.usuario = :usuario
'''

# a senha vale para o portal e todos os módulos (mesmo cadastro)
CADASTRAR_SENHA = '''
	UPDATE nexus.usuarios u
	SET senha_hash = :senha_hash,
		senha_definida_em = now()
	WHERE u.id = :id
	AND u.senha_hash IS NULL
	AND u.ativo
	AND EXISTS (
		SELECT 1 FROM nexus.usuario_modulos um
		WHERE um.id_usuario = u.id AND um.modulo = 'financiamento'
	)
'''
