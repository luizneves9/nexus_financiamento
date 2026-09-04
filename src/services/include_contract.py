import streamlit as st
import pandas as pd
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_gerais import INCLUIR_CONTRATO, SELECT_CONTRATOS
from repositories.include_antecipation import registrar_contrato, consultar_contratos

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def incluir_contrato(session_state):
    '''Processo de inclusão de contrato, incluindo regras de negócios.'''

    # validando preenchimento das colunas
    campos_nao_preenchidos = []
    for key, val in session_state.items():
        if val is None or str(val) == '':
            key = f'{key}'.replace('ic_', '').replace('_', ' ').title()
            campos_nao_preenchidos.append(key)

    if campos_nao_preenchidos:
        session_state['mensagem_erro'] = f'Preencha todos os campos! {', '.join(campos_nao_preenchidos)}'
        return

    # validando valores incluidos
    if session_state['ic_dt_bndes'] < session_state['ic_dt_emissao']:
        session_state['mensagem_erro'] = f'A data BNDES deve ser maior ou igual que a data de emissão.'
        return

    if session_state['ic_valor_financiado'] <= 0:
        session_state['mensagem_erro'] = f'O valor financiado deve ser maior que zero!'
        return

    if session_state['ic_taxa_juros_efetiva'] <= 0:
        session_state['mensagem_erro'] = f'O juros total deve ser maior que zero!'
        return

    if session_state['ic_prazo_total'] <= 0:
        session_state['mensagem_erro'] = f'O prazo total deve ser maior que zero!'
        return

    if session_state['ic_prazo_carencia'] <= 0:
        session_state['mensagem_erro'] = f'O prazo de carência deve ser maior que zero!'
        return

    if session_state['ic_prazo_final'] <= 0:
        session_state['mensagem_erro'] = f'O prazo final deve ser maior que zero!'
        return

    if session_state['ic_prazo_final'] < 0:
        session_state['mensagem_erro'] = f'O pagamento de carência deve ser maior ou igual a zero!'
        return

    if session_state['ic_dt_primeiro_encargo'] <= session_state['ic_dt_emissao']:
        session_state['mensagem_erro'] = f'A data do primeiro encargo deve ser maior que a data de emissão do contrato!'
        return

    if session_state['ic_dt_primeiro_principal'] <= session_state['ic_dt_primeiro_encargo']:
        session_state['mensagem_erro'] = f'A data do primeiro principal deve ser maior que a data do primeiro encargo!'
        return

    if session_state['ic_dt_ultima_parcela'] <= session_state['ic_dt_primeiro_principal']:
        session_state['mensagem_erro'] = f'A data da última parcela deve ser maior que a data do primeiro principal!'
        return

    # definindo e ajustando parâmetros
    id_empresa = int(session_state['df_lista_empresas'].loc[session_state['df_lista_empresas']['razao_social'] == session_state['ic_empresas'], 'id'].iloc[0])
    id_banco = int(session_state['df_lista_bancos'].loc[session_state['df_lista_bancos']['razao_social'] == session_state['ic_bancos'], 'id'].iloc[0])
    debito_em_conta = True if session_state['ic_debito_cc'] == 'SIM' else False

    # definindo os parâmetros
    parametro = {
        'id_empresa': id_empresa,
        'id_banco': id_banco,
        'contrato': session_state['ic_numero_contrato'],
        'data_emissao': session_state['ic_dt_emissao'],
        'data_bndes': session_state['ic_dt_bndes'],
        'tipo': session_state['ic_tipo'],
        'valor': session_state['ic_valor_financiado'],
        'pos_fixado': session_state['ic_pos_fixado'],
        'custo_bndes': session_state['ic_custo_bndes'],
        'sobretaxa_bndes': session_state['ic_sobretaxa_bndes'],
        'juros_banco': session_state['ic_taxa_banco'],
        'juros_total': session_state['ic_taxa_juros_efetiva'],
        'prazo_total': session_state['ic_prazo_total'],
        'prazo_carencia': session_state['ic_prazo_carencia'],
        'prazo_final': session_state['ic_prazo_final'],
        'data_primeira_parcela_encargo': session_state['ic_dt_primeiro_encargo'],
        'data_primeira_parcela_prestacao': session_state['ic_dt_primeiro_principal'],
        'data_ultima_parcela': session_state['ic_dt_ultima_parcela'],
        'debito_conta_corrente': debito_em_conta,
        'carencia_pagamento': session_state['ic_pagamento_carencia'],
        'registro_cobranca': session_state['ic_registro_cobranca']
    }

    # definindo a query
    query = text(INCLUIR_CONTRATO)

    # conexão com o banco de dados
    try:
        with engine.begin() as conn:
            registrar_contrato(query, conn, parametro)
        st.session_state['mensagem_sucesso'] = 'Contrato incluído com sucesso!'
        st.rerun()
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao incluir contrato. ({e})'
        st.rerun()

def listar_contratos():
    '''Função definida para listar todos os contratos registrados no banco de dados.'''

    df = pd.DataFrame()
    query = SELECT_CONTRATOS

    try:
        with engine.begin() as conn:
            df = consultar_contratos(query, conn)
    except:
        pass

    return df
