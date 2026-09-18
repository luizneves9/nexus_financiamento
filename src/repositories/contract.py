import pandas as pd

def listar_projecao(query, conn, parametros):
    '''Interação com o banco de dados para importar dataframe com projeção dos valores.'''
    return pd.read_sql(sql=query, con=conn, params=parametros)

def listar_contratos(query, conn, parametros):
    '''Interação com o banco de dados para importar dataframe de contratos com filtros opcionais.'''
    return pd.read_sql(sql=query, con=conn, params=parametros)

def interacao_database(query, conn, parametro):
    '''Interação com banco de dados.'''
    return conn.execute(query, parametro)