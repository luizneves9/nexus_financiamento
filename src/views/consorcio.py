import pandas as pd
import streamlit as st
from datetime import date
from services.consorcio import (
    PAGO,
    A_PAGAR,
    listar_consorcio_pago,
    listar_consorcio_a_pagar,
    listar_consorcio_credito,
    competencia_do_mes,
)
from tools.funcoes import transformar_float_em_str
from views.components.cabecalho import cabecalho
from views.components.modal_consorcio_importar import modal_consorcio_importar
from views.components.modal_consorcio_credito import modal_consorcio_credito

def formatar_valores(df, colunas):
    '''Valores monetários no formato brasileiro (vazio fica em branco).'''
    for coluna in colunas:
        df[coluna] = df[coluna].map(lambda v: transformar_float_em_str(float(v)) if pd.notna(v) else None)

def aba_pago():
    '''Pagamentos de consórcio pelo período da data de pagamento.'''

    with st.form('consorcio_pago_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            data_ini = st.date_input('Pagamento de', key='fco_pago_ini_input', format='DD/MM/YYYY')
            data_fim = st.date_input('Pagamento até', key='fco_pago_fim_input', format='DD/MM/YYYY')
            banco = st.text_input('Banco', key='fco_pago_banco_input')
            consorciado = st.text_input('Consorciado', key='fco_pago_consorciado_input')
            proposta = st.text_input('Proposta', key='fco_pago_proposta_input')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fco_pago_ini'] = data_ini
            st.session_state['fco_pago_fim'] = data_fim
            st.session_state['fco_pago_banco'] = banco or None
            st.session_state['fco_pago_consorciado'] = consorciado or None
            st.session_state['fco_pago_proposta'] = proposta or None

    with st.spinner('Consultando pagamentos de consórcio...'):
        df = listar_consorcio_pago(st.session_state['fco_pago_ini'], st.session_state['fco_pago_fim'],
                                   st.session_state['fco_pago_banco'], st.session_state['fco_pago_consorciado'],
                                   st.session_state['fco_pago_proposta'])

    if df.empty:
        st.warning('Nenhum pagamento de consórcio encontrado com os filtros aplicados.')
        return

    # resumo calculado antes da formatação
    registros, total, propostas = len(df), float(df['valor_total'].sum()), df['numero_proposta'].nunique()

    formatar_valores(df, ['valor_fundo_comum', 'valor_fundo_reserva', 'valor_taxa_administracao',
                          'valor_multa_juros', 'valor_outros', 'valor_total'])
    df.insert(0, 'sel', False)

    st.data_editor(
        df,
        width='content',
        hide_index=True,
        disabled=True,
        column_config={
            'sel': st.column_config.CheckboxColumn('', default=False),
            'id': None,
            'banco': 'Banco',
            'nome_consorciado': 'Consorciado',
            'numero_proposta': 'Proposta',
            'id_cota': 'Cota',
            'data_adesao': st.column_config.DateColumn('Adesão', format='DD/MM/YYYY'),
            'movimento': 'Movimento',
            'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
            'valor_fundo_comum': 'Fundo comum',
            'valor_fundo_reserva': 'Fundo reserva',
            'valor_taxa_administracao': 'Taxa adm.',
            'valor_multa_juros': 'Multa e juros',
            'valor_outros': 'Outros',
            'valor_total': 'Total',
            'nome_arquivo': 'Arquivo',
            'usuario': 'Usuário',
            'data_registro': st.column_config.DatetimeColumn('Importado em', format='DD/MM/YYYY HH:mm'),
        }
    )

    st.caption(
        f"**Registros:** {registros}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Propostas:** {propostas}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Total pago:** R\\$ {transformar_float_em_str(total)}",
        unsafe_allow_html=True
    )

def aba_a_pagar():
    '''Parcelas a pagar de consórcio da competência (data base) filtrada.'''

    with st.form('consorcio_a_pagar_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            data_base = st.date_input('Data base', key='fco_apagar_data_base_input', format='DD/MM/YYYY')
            banco = st.text_input('Banco', key='fco_apagar_banco_input')
            consorciado = st.text_input('Consorciado', key='fco_apagar_consorciado_input')
            proposta = st.text_input('Proposta', key='fco_apagar_proposta_input')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fco_apagar_data_base'] = data_base
            st.session_state['fco_apagar_banco'] = banco or None
            st.session_state['fco_apagar_consorciado'] = consorciado or None
            st.session_state['fco_apagar_proposta'] = proposta or None

    competencia = competencia_do_mes(st.session_state['fco_apagar_data_base'])
    with st.spinner('Consultando parcelas a pagar de consórcio...'):
        df = listar_consorcio_a_pagar(competencia, st.session_state['fco_apagar_banco'],
                                      st.session_state['fco_apagar_consorciado'], st.session_state['fco_apagar_proposta'])

    if df.empty:
        st.warning(f'Nenhuma parcela a pagar de consórcio importada para a competência {competencia:%m/%Y} com os filtros aplicados.')
        return

    # resumo calculado antes da formatação
    registros, total = len(df), float(df['valor_parcela'].sum())
    propostas, bancos, consorciados = df['numero_proposta'].nunique(), df['banco'].nunique(), df['nome_consorciado'].nunique()

    formatar_valores(df, ['valor_parcela'])
    df.insert(0, 'sel', False)

    st.data_editor(
        df,
        width='content',
        hide_index=True,
        disabled=True,
        column_config={
            'sel': st.column_config.CheckboxColumn('', default=False),
            'id': None,
            'competencia': st.column_config.DateColumn('Competência', format='MM/YYYY'),
            'banco': 'Banco',
            'nome_consorciado': 'Consorciado',
            'numero_proposta': 'Proposta',
            'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
            'valor_parcela': 'Valor parcela',
            'data_emissao': st.column_config.DateColumn('Emissão', format='DD/MM/YYYY'),
            'nome_arquivo': 'Arquivo',
            'usuario': 'Usuário',
            'data_registro': st.column_config.DatetimeColumn('Importado em', format='DD/MM/YYYY HH:mm'),
        }
    )

    st.caption(
        f"**Competência:** {competencia:%m/%Y}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Bancos:** {bancos}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Consorciados:** {consorciados}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Propostas:** {propostas}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Parcelas:** {registros}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Total a pagar:** R\\$ {transformar_float_em_str(total)}",
        unsafe_allow_html=True
    )

def aba_creditos():
    '''Créditos de consórcio lançados por competência.'''

    with st.spinner('Consultando créditos de consórcio...'):
        df = listar_consorcio_credito()

    if df.empty:
        st.warning('Nenhum crédito de consórcio lançado.')
        return

    formatar_valores(df, ['credito_cotas_contempladas', 'credito_parcelas_nao_contempladas'])
    df.insert(0, 'sel', False)

    st.data_editor(
        df,
        width='content',
        hide_index=True,
        disabled=True,
        column_config={
            'sel': st.column_config.CheckboxColumn('', default=False),
            'id': None,
            'competencia': st.column_config.DateColumn('Competência', format='MM/YYYY'),
            'credito_cotas_contempladas': 'Crédito cotas contempladas',
            'credito_parcelas_nao_contempladas': 'Crédito parcelas pagas e não contempladas',
            'usuario': 'Usuário',
            'data_registro': st.column_config.DatetimeColumn('Lançado em', format='DD/MM/YYYY HH:mm'),
            'data_alteracao': st.column_config.DatetimeColumn('Alterado em', format='DD/MM/YYYY HH:mm'),
        }
    )

    st.caption(f'**Competências lançadas:** {len(df)}', unsafe_allow_html=True)

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Consórcio', 'Pagamentos e parcelas a pagar importados por banco e consorciado, e créditos do fechamento.', 'request_quote')

    # inicializar session_states dos filtros (FCO = Filtro Consórcio); padrão: pagamentos do ano atual, data base = hoje
    hoje = date.today()
    padroes = {
        'fco_pago_ini': hoje.replace(month=1, day=1),
        'fco_pago_fim': hoje,
        'fco_pago_banco': None,
        'fco_pago_consorciado': None,
        'fco_pago_proposta': None,
        'fco_apagar_data_base': hoje,
        'fco_apagar_banco': None,
        'fco_apagar_consorciado': None,
        'fco_apagar_proposta': None,
    }
    for chave, valor in padroes.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

    # inicializar session_states dos widgets a partir dos filtros salvos
    # (o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado)
    for chave in padroes:
        if f'{chave}_input' not in st.session_state:
            valor = st.session_state[chave]
            st.session_state[f'{chave}_input'] = '' if valor is None else valor

    # botões de interação
    with st.container(horizontal=True):
        if st.button('Importar pago'): modal_consorcio_importar(PAGO, st.session_state['fco_apagar_data_base'])
        if st.button('Importar a pagar'): modal_consorcio_importar(A_PAGAR, st.session_state['fco_apagar_data_base'])
        if st.button('Créditos'): modal_consorcio_credito(st.session_state['fco_apagar_data_base'])

    aba_1, aba_2, aba_3 = st.tabs(['Pago', 'A pagar', 'Créditos'])
    with aba_1:
        aba_pago()
    with aba_2:
        aba_a_pagar()
    with aba_3:
        aba_creditos()

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
