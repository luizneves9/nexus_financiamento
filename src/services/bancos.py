import pandas as pd
from database.connection import ConexaoBancoSQL
from queries.queries_bancos import SELECT_BANCOS
from repositories.funcoes import ler_query

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_bancos():
    '''Função definida para listar todas as empresas registrados no banco de dados.'''

    df = pd.DataFrame()
    query = SELECT_BANCOS

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn)
    except:
        pass

    return df
