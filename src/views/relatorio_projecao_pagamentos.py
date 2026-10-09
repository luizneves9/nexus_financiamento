import streamlit as st
from services.relatorio_projecao_pagamentos import listar_projecao_pagamentos, resumir_projecao_pagamentos
from tools.funcoes import transformar_float_em_str
from views.components.cabecalho import cabecalho

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Projeção de Pagamentos', 'Agrupamento da projeção de pagamentos dos contratos.', 'bar_chart')

    # inicializar session_states dos filtros (FP = Filtro Projeção)
    if 'fp_empresa' not in st.session_state:
        st.session_state['fp_empresa'] = None
    if 'fp_banco' not in st.session_state:
        st.session_state['fp_banco'] = None
    if 'fp_contrato' not in st.session_state:
        st.session_state['fp_contrato'] = None
    if 'fp_data_vcto_ini' not in st.session_state:
        st.session_state['fp_data_vcto_ini'] = None
    if 'fp_data_vcto_fim' not in st.session_state:
        st.session_state['fp_data_vcto_fim'] = None

    # inicializar session_states dos widgets a partir dos filtros salvos
    # (o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado)
    if 'fp_empresa_input' not in st.session_state:
        st.session_state['fp_empresa_input'] = st.session_state['fp_empresa'] or ''
    if 'fp_banco_input' not in st.session_state:
        st.session_state['fp_banco_input'] = st.session_state['fp_banco'] or ''
    if 'fp_contrato_input' not in st.session_state:
        st.session_state['fp_contrato_input'] = st.session_state['fp_contrato'] or ''
    if 'fp_data_vcto_ini_input' not in st.session_state:
        st.session_state['fp_data_vcto_ini_input'] = st.session_state['fp_data_vcto_ini']
    if 'fp_data_vcto_fim_input' not in st.session_state:
        st.session_state['fp_data_vcto_fim_input'] = st.session_state['fp_data_vcto_fim']

    # lista de filtros
    with st.form('projecao_pagamentos_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            empresa = st.text_input('Empresa', key='fp_empresa_input')
            banco = st.text_input('Banco', key='fp_banco_input')
            contrato = st.text_input('Contrato', key='fp_contrato_input')
            data_vcto_ini = st.date_input('Vcto de', key='fp_data_vcto_ini_input', format='DD/MM/YYYY')
            data_vcto_fim = st.date_input('Vcto até', key='fp_data_vcto_fim_input', format='DD/MM/YYYY')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fp_empresa'] = empresa if empresa else None
            st.session_state['fp_banco'] = banco if banco else None
            st.session_state['fp_contrato'] = contrato if contrato else None
            st.session_state['fp_data_vcto_ini'] = data_vcto_ini
            st.session_state['fp_data_vcto_fim'] = data_vcto_fim

    # listando projeção de pagamentos com filtros
    with st.spinner('Consultando projeção de pagamentos...'):
        df_projecao = listar_projecao_pagamentos(
            empresa=st.session_state.get('fp_empresa'),
            banco=st.session_state.get('fp_banco'),
            contrato=st.session_state.get('fp_contrato'),
            data_vcto_ini=st.session_state.get('fp_data_vcto_ini'),
            data_vcto_fim=st.session_state.get('fp_data_vcto_fim')
        )

    if df_projecao.empty:
        st.warning('Nenhuma projeção encontrada com os filtros aplicados.')
        return

    # resumo calculado antes da formatação (valores ainda numéricos)
    resumo = resumir_projecao_pagamentos(df_projecao)

    # definindo formato
    for coluna in ('valor_principal', 'valor_juros', 'parcela_h', 'total_parcela'):
        df_projecao[coluna] = df_projecao[coluna].map(transformar_float_em_str)

    # inclusão da opção de seleção
    df_projecao.insert(0, 'sel', False)

    # visualização do dataframe
    df_visual = st.data_editor(
        df_projecao,
        width='content',
        hide_index=True,
        column_config={
            'sel': st.column_config.CheckboxColumn('', default=False),
            'data_emissao': st.column_config.DateColumn(format='DD/MM/YYYY'),
            'data': st.column_config.DateColumn(format='DD/MM/YYYY'),
            'data_vcto': st.column_config.DateColumn(format='DD/MM/YYYY'),
        }
    )

    # resumo de valores
    st.caption(
        f"**Empresas:** {resumo['empresas']}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Bancos:** {resumo['bancos']}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Contratos:** {resumo['contratos']}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Total das parcelas:** R$ {transformar_float_em_str(resumo['total_parcela'])}",
        unsafe_allow_html=True
    )

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
