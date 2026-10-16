import pandas as pd
import streamlit as st
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_antecipacao import SELECT_ANTECIPACOES, DELETE_ANTECIPACAO
from repositories.funcoes import ler_query
from repositories.contract import interacao_database
from services.log import registrar_log, registrar_log_falha, ANTECIPACAO_EXCLUIR

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def listar_antecipacoes(empresa=None, banco=None, contrato=None, data_pagamento_ini=None, data_pagamento_fim=None):
    '''Função definida para listar as antecipações/quitações registradas com filtros opcionais.'''

    df = pd.DataFrame()
    query = text(SELECT_ANTECIPACOES)
    parametros = {
        'empresa': empresa or None,      # valor exato do selectbox (razão social)
        'banco': banco or None,
        'contrato': f"%{contrato}%" if contrato else None,
        'data_pagamento_ini': data_pagamento_ini,
        'data_pagamento_fim': data_pagamento_fim
    }

    try:
        with engine.begin() as conn:
            df = ler_query(query, conn, parametros)
    except:
        pass

    return df

def resumir_antecipacoes(df):
    '''Função definida para resumir as antecipações filtradas (quantidades e total pago).'''

    return {
        'empresas': df['nome_empresa'].nunique(),
        'bancos': df['banco'].nunique(),
        'contratos': df['numero_contrato'].nunique(),
        'valor_pago': float(df['valor_pago'].sum())
    }

def excluir_antecipacao_banco(id_antecipacao):
    '''Exclui a antecipação/quitação; o trigger do banco recalcula a projeção do contrato.'''

    query = text(DELETE_ANTECIPACAO)
    parametro = {'id': id_antecipacao}

    try:
        # DELETE ... RETURNING devolve o lançamento excluído, gravado no log na mesma transação
        with engine.begin() as conn:
            excluido = interacao_database(query, conn, parametro).mappings().first()

            if excluido is None:
                st.session_state['mensagem_erro'] = 'Lançamento não encontrado.'
                return

            registrar_log(ANTECIPACAO_EXCLUIR, 'antecipacao', id_antecipacao,
                          detalhes=dict(excluido), conn=conn)

        st.session_state['mensagem_sucesso'] = 'Lançamento excluído e projeção do contrato recalculada!'

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(ANTECIPACAO_EXCLUIR, erro, 'antecipacao', id_antecipacao)
        st.session_state['mensagem_erro'] = f'Erro ao excluir lançamento. ({erro})'
