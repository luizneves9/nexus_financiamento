import calendar
import pandas as pd
import streamlit as st
from datetime import date
from services.relatorio_contas_a_pagar import (
    listar_contas_a_pagar,
    resumir_contas_a_pagar,
    exportar_contas_a_pagar,
    COLUNAS_CONTAS_A_PAGAR,
    COLUNAS_VALOR,
)
from tools.funcoes import transformar_float_em_str
from views.components.cabecalho import cabecalho

# opções do filtro de situação (rótulo na tela -> valor na consulta)
SITUACOES = {'Todas': None, 'Liquidado': 'Liquidado', 'Projetado': 'Projetado', 'Antecipação': 'Antecipação', 'Quitação': 'Quitação'}

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Contas a Pagar', 'Posição na data base: parcelas pagas pelo valor pago e demais pelo valor projetado.', 'bar_chart')

    # inicializar session_states dos filtros (FCP = Filtro Contas a Pagar); padrão: data base hoje e vencimentos do mês atual
    hoje = date.today()
    if 'fcp_data_base' not in st.session_state:
        st.session_state['fcp_data_base'] = hoje
    if 'fcp_empresa' not in st.session_state:
        st.session_state['fcp_empresa'] = None
    if 'fcp_banco' not in st.session_state:
        st.session_state['fcp_banco'] = None
    if 'fcp_contrato' not in st.session_state:
        st.session_state['fcp_contrato'] = None
    if 'fcp_data_vcto_ini' not in st.session_state:
        st.session_state['fcp_data_vcto_ini'] = hoje.replace(day=1)
    if 'fcp_data_vcto_fim' not in st.session_state:
        st.session_state['fcp_data_vcto_fim'] = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])
    if 'fcp_situacao' not in st.session_state:
        st.session_state['fcp_situacao'] = 'Todas'

    # inicializar session_states dos widgets a partir dos filtros salvos
    # (o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado)
    if 'fcp_data_base_input' not in st.session_state:
        st.session_state['fcp_data_base_input'] = st.session_state['fcp_data_base']
    if 'fcp_empresa_input' not in st.session_state:
        st.session_state['fcp_empresa_input'] = st.session_state['fcp_empresa'] or ''
    if 'fcp_banco_input' not in st.session_state:
        st.session_state['fcp_banco_input'] = st.session_state['fcp_banco'] or ''
    if 'fcp_contrato_input' not in st.session_state:
        st.session_state['fcp_contrato_input'] = st.session_state['fcp_contrato'] or ''
    if 'fcp_data_vcto_ini_input' not in st.session_state:
        st.session_state['fcp_data_vcto_ini_input'] = st.session_state['fcp_data_vcto_ini']
    if 'fcp_data_vcto_fim_input' not in st.session_state:
        st.session_state['fcp_data_vcto_fim_input'] = st.session_state['fcp_data_vcto_fim']
    if 'fcp_situacao_input' not in st.session_state:
        st.session_state['fcp_situacao_input'] = st.session_state['fcp_situacao']

    # lista de filtros
    with st.form('contas_a_pagar_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            data_base = st.date_input('Data base', key='fcp_data_base_input', format='DD/MM/YYYY')
            empresa = st.text_input('Empresa', key='fcp_empresa_input')
            banco = st.text_input('Banco', key='fcp_banco_input')
            contrato = st.text_input('Contrato', key='fcp_contrato_input')
            data_vcto_ini = st.date_input('Vcto de', key='fcp_data_vcto_ini_input', format='DD/MM/YYYY')
            data_vcto_fim = st.date_input('Vcto até', key='fcp_data_vcto_fim_input', format='DD/MM/YYYY')
            situacao = st.selectbox('Situação', list(SITUACOES), key='fcp_situacao_input')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fcp_data_base'] = data_base or hoje
            st.session_state['fcp_empresa'] = empresa if empresa else None
            st.session_state['fcp_banco'] = banco if banco else None
            st.session_state['fcp_contrato'] = contrato if contrato else None
            st.session_state['fcp_data_vcto_ini'] = data_vcto_ini
            st.session_state['fcp_data_vcto_fim'] = data_vcto_fim
            st.session_state['fcp_situacao'] = situacao

    # listando contas a pagar com filtros
    data_base = st.session_state['fcp_data_base']
    with st.spinner('Consultando contas a pagar...'):
        df_contas = listar_contas_a_pagar(
            data_base,
            empresa=st.session_state.get('fcp_empresa'),
            banco=st.session_state.get('fcp_banco'),
            contrato=st.session_state.get('fcp_contrato'),
            data_vcto_ini=st.session_state.get('fcp_data_vcto_ini'),
            data_vcto_fim=st.session_state.get('fcp_data_vcto_fim'),
            situacao=SITUACOES[st.session_state.get('fcp_situacao')]
        )

    if df_contas.empty:
        st.warning('Nenhuma conta a pagar encontrada com os filtros aplicados.')

    else:
        # resumo e arquivo de exportação gerados antes da formatação (valores ainda numéricos)
        resumo = resumir_contas_a_pagar(df_contas)
        conteudo, nome_arquivo, tipo_arquivo = exportar_contas_a_pagar(df_contas, data_base)

        # definindo formato (valores vazios ficam em branco)
        for coluna in COLUNAS_VALOR:
            df_contas[coluna] = df_contas[coluna].map(lambda v: transformar_float_em_str(v) if pd.notna(v) else None)

        # inclusão da opção de seleção
        df_contas.insert(0, 'sel', False)

        # visualização do dataframe
        st.data_editor(
            df_contas,
            width='content',
            hide_index=True,
            disabled=[coluna for coluna in df_contas.columns if coluna != 'sel'],
            column_config={
                'sel': st.column_config.CheckboxColumn('', default=False),
                **COLUNAS_CONTAS_A_PAGAR,
                'vencimento': st.column_config.DateColumn('Vencimento', format='DD/MM/YYYY'),
                'vencimento_util': st.column_config.DateColumn('Vencimento útil', format='DD/MM/YYYY'),
                'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
            }
        )

        # linha de ações
        with st.container(horizontal=True):
            st.download_button('Exportar', data=conteudo, file_name=nome_arquivo, mime=tipo_arquivo)

        # resumo de valores (valor considerado por situação)
        st.caption(
            f"**Data base:** {data_base:%d/%m/%Y}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Contratos:** {resumo['contratos']}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Linhas:** {resumo['linhas']}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Liquidado:** R\\$ {transformar_float_em_str(resumo['liquidado'])}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Antecipações/Quitações:** R\\$ {transformar_float_em_str(resumo['antecipacoes'])}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Projetado:** R\\$ {transformar_float_em_str(resumo['projetado'])}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Total considerado:** R\\$ {transformar_float_em_str(resumo['total'])}",
            unsafe_allow_html=True
        )

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
