def buscar_usuario(query, conn, parametros):
    '''Interação com o banco de dados para retornar um usuário (ou None).'''
    return conn.execute(query, parametros).mappings().first()

def atualizar_usuario(query, conn, parametros):
    '''Interação com o banco de dados para atualizar um usuário; retorna as linhas afetadas.'''
    return conn.execute(query, parametros).rowcount
