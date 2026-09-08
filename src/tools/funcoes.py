import streamlit as st
from queries.queries_gerais import SELECT_EMPRESAS, SELECT_BANCOS
from database.connection import ConexaoBancoSQL
from repositories.funcoes import ler_query

connection = ConexaoBancoSQL()
engine = connection.conexao_banco()

def listar_empresas():
    '''Listar todas as empresas cadastradas no banco de dados.'''

    query = SELECT_EMPRESAS
    try:
        with engine.begin() as conn:
            df = ler_query(query, conn)
            return df
    except Exception as e:
        st.session_state.mensagem_erro = f'Erro ao carregar empresas ({e}).'

def listar_bancos():
    '''Listar todas os bancos cadastradas no banco de dados.'''

    query = SELECT_BANCOS
    try:
        with engine.begin() as conn:
            df = ler_query(query, conn)
            return df
    except Exception as e:
        st.session_state.mensagem_erro = f'Erro ao carregar bancos ({e}).'

def incluir_contrato(session_state):
    '''Função para incluir novo contrato.'''

def transformar_float_em_str(valor):
    '''Função para transformar valores em formato brasileiro.'''

    if isinstance(valor, str):
        return str

    if isinstance(valor, (float, int)):
        return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')
