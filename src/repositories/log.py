def inserir_log(query, conn, parametros):
    '''Interação com o banco de dados para inserir um registro no log de auditoria.'''
    conn.execute(query, parametros)
