import streamlit as st
from tools.funcoes import listar_empresas, listar_bancos
from src.services.contracts import incluir_contrato

def inicializar_state():
    '''Inicializar state do servidor.'''

    # carregando empresas
    if 'df_lista_empresas' not in st.session_state or st.session_state.df_lista_empresas is None:
        st.session_state.df_lista_empresas = listar_empresas()

    df = st.session_state.df_lista_empresas

    if df is not None and 'razao_social' in df:
        empresas = df['razao_social'].to_list()
    else:
        empresas = []

    # carregando bancos
    if 'df_lista_bancos' not in st.session_state or st.session_state.df_lista_bancos is None:
        st.session_state.df_lista_bancos = listar_bancos()

    df = st.session_state.df_lista_bancos

    if df is not None and 'razao_social' in df:
        bancos = df['razao_social'].to_list()
    else:
        bancos = []

    # definindo os dados padrões de cara armazenamento
    default = {
        'ic_empresas': empresas,
        'ic_bancos': bancos,
        'ic_numero_contrato': None,
        'ic_dt_emissao': None,
        'ic_dt_bndes': None,
        'ic_tipo': ['BNDES FINAME SELIC'],
        'ic_valor_financiado': 0.00,
        'ic_pos_fixado': ['SELIC'],
        'ic_custo_bndes': 0.00,
        'ic_sobretaxa_bndes': 0.00,
        'ic_taxa_banco': 0.00,
        'ic_taxa_juros_efetiva': 0.00,
        'ic_prazo_total': 0,
        'ic_prazo_carencia': 0,
        'ic_prazo_final': 0,
        'ic_pagamento_carencia': 0,
        'ic_dt_primeiro_encargo': None,
        'ic_dt_primeiro_principal': None,
        'ic_dt_ultima_parcela': None,
        'ic_debito_cc': ['NAO', 'SIM'],
        'ic_registro_cobranca': ['PRIMEIRO_DIA_UTIL', 'VENCIMENTO']
    }

    for key, val in default.items():
        if not key in st.session_state:
            st.session_state[key] = val

@st.dialog('Inclusão de Novos Contratos', width='large', dismissible=False)
def modal_incluir_contrato():

    # inicializando as variáveis de armazenamento
    inicializar_state()

    # formulário de interação
    with st.form('contract', border=False):

        c1, c2, c3, c4 = st.columns([1, 1.5, 1.5, 1])

        c1.selectbox('Empresa', st.session_state.df_lista_empresas['razao_social'], key='ic_empresas')
        c2.selectbox('Banco', st.session_state.df_lista_bancos['razao_social'], key='ic_bancos')
        c3.text_input('Número do Contrato', st.session_state.ic_numero_contrato, key='ic_numero_contrato')
        c4.date_input('Data Emissão', format='DD/MM/YYYY', value=st.session_state.ic_dt_emissao, key='ic_dt_emissao')

        c5, c6, c7, c8 = st.columns([1, 1.5, 1.5, 1])

        c5.date_input('Data BNDES', value=st.session_state.ic_dt_bndes, format='DD/MM/YYYY', key='ic_dt_bndes')
        c6.selectbox('Tipo', st.session_state.ic_tipo, key='ic_tipo')
        c7.number_input('Valor financiado', st.session_state.ic_valor_financiado, key='ic_valor_financiado')
        c8.selectbox('Pós fixado', st.session_state.ic_pos_fixado, key='ic_pos_fixado')

        c9, c10, c11, c12 = st.columns([1, 1, 1, 1])

        c9.number_input('Custo bndes (%)', st.session_state.ic_custo_bndes, key='ic_custo_bndes')
        c10.number_input('Sobretaxa bndes (%)', st.session_state.ic_sobretaxa_bndes, key='ic_sobretaxa_bndes')
        c11.number_input('Taxa banco (%)', st.session_state.ic_taxa_banco, key='ic_taxa_banco')
        c12.number_input('Taxa juros efetiva (%)', st.session_state.ic_taxa_juros_efetiva, key='ic_taxa_juros_efetiva')

        c13, c14, c15, c16 = st.columns([1, 1, 1, 1])
        
        c13.number_input('Prazo total', st.session_state.ic_prazo_total, key='ic_prazo_total')
        c14.number_input('Prazo carência', st.session_state.ic_prazo_carencia, key='ic_prazo_carencia')
        c15.number_input('Prazo final', st.session_state.ic_prazo_final, key='ic_prazo_final')
        c16.number_input('Pagamento de carência', st.session_state.ic_pagamento_carencia, key='ic_pagamento_carencia')

        c17, c18, c19, c20, c21 = st.columns([1, 1, 1, 1, 1])
        
        c17.date_input('Data primeira parcela de encargo', value=st.session_state.ic_dt_primeiro_encargo, format='DD/MM/YYYY', key='ic_dt_primeiro_encargo')
        c18.date_input('Data primeira parcela do principal', value=st.session_state.ic_dt_primeiro_principal, format='DD/MM/YYYY', key='ic_dt_primeiro_principal')
        c19.date_input('Data ultima parcela', value=st.session_state.ic_dt_ultima_parcela, format='DD/MM/YYYY', key='ic_dt_ultima_parcela')
        c20.selectbox('Débito em cc', st.session_state.ic_debito_cc, key='ic_debito_cc')
        c21.selectbox('Registro de cobrança', st.session_state.ic_registro_cobranca, key='ic_registro_cobranca')

        with st.container(horizontal=True):
            if st.form_submit_button('Confirmar'):
                incluir_contrato(st.session_state)

            if st.form_submit_button('Cancelar'):
                st.rerun()
            
        ## notificações
        if 'mensagem_sucesso' in st.session_state:
            st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')
            inicializar_state()
            st.rerun()

        if 'mensagem_erro' in st.session_state:
            st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')
