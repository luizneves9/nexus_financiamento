# Anexos (PDF) dos contratos: uma tabela por tipo. As consultas de lista nunca leem o conteúdo (bytea).

# tipo -> tabela
TABELAS_ANEXO = {
    'CONTRATO': 'financiamento.anexo_contrato',
    'FICHA_FINANCEIRA': 'financiamento.anexo_ficha_financeira',
}

SELECT_ANEXOS = {
    tipo: f'''
	SELECT id, nome_arquivo, tamanho_bytes, usuario, data_registro
	FROM {tabela}
	WHERE id_contrato = :id_contrato
	ORDER BY data_registro, id
'''
    for tipo, tabela in TABELAS_ANEXO.items()
}

SELECT_CONTEUDO_ANEXO = {
    tipo: f'''
	SELECT nome_arquivo, conteudo
	FROM {tabela}
	WHERE id = :id
'''
    for tipo, tabela in TABELAS_ANEXO.items()
}

INSERIR_ANEXO = {
    tipo: f'''
	INSERT INTO {tabela} (id_contrato, nome_arquivo, tamanho_bytes, hash_sha256, conteudo, usuario)
	VALUES (:id_contrato, :nome_arquivo, :tamanho_bytes, :hash_sha256, :conteudo, :usuario)
	RETURNING id, id_contrato, nome_arquivo, tamanho_bytes, hash_sha256, usuario, data_registro
'''
    for tipo, tabela in TABELAS_ANEXO.items()
}

EXCLUIR_ANEXO = {
    tipo: f'''
	DELETE FROM {tabela}
	WHERE id = :id
	RETURNING id, id_contrato, nome_arquivo, tamanho_bytes, hash_sha256, usuario, data_registro
'''
    for tipo, tabela in TABELAS_ANEXO.items()
}

# anexos que serão excluídos junto com o contrato (para o log da exclusão do contrato)
SELECT_ANEXOS_DO_CONTRATO = '''
	SELECT 'CONTRATO' AS tipo, nome_arquivo, tamanho_bytes, hash_sha256
	FROM financiamento.anexo_contrato WHERE id_contrato = :id
	UNION ALL
	SELECT 'FICHA_FINANCEIRA', nome_arquivo, tamanho_bytes, hash_sha256
	FROM financiamento.anexo_ficha_financeira WHERE id_contrato = :id
'''
