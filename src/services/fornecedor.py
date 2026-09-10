import pandas as pd
from database.connection import ConexaoBancoSQL
from repositories.funcoes import ler_query
from queries.queries_fornecedores import SELECT_FORNECEDORES

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_fornecedores():
    '''Função definida para listar todas as empresas registrados no banco de dados.'''

    df = pd.DataFrame()
    query = SELECT_FORNECEDORES

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn)
    except:
        pass

    return df
