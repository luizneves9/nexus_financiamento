import pandas as pd
from database.connection import ConexaoBancoSQL
from queries.queries_empresas import SELECT_EMPRESAS
from repositories.empresas import consultar_empresas

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_empresas():
    '''Função definida para listar todas as empresas registrados no banco de dados.'''

    df = pd.DataFrame()
    query = SELECT_EMPRESAS

    try:
        with engine.begin() as conn:
            df = consultar_empresas(query, conn)
    except:
        pass

    return df
