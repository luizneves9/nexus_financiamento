import streamlit as st
from services.include_antecipation import listar_antecipacoes, resumir_antecipacoes
from tools.funcoes import transformar_float_em_str

def main():

    # definindo o título da página
    st.markdown('''
        <h2 style='margin-bottom: 0px;'>Antecipações</h2>
        <p style='margin-top: -15px; color: #666; font-style: italic;'>
            Visualização das antecipações e quitações registradas nos contratos.
        </p>
        ''',
        unsafe_allow_html=True
    )

    # inicializar session_states dos filtros (FA = Filtro Antecipação)
    if 'fa_empresa' not in st.session_state:
        st.session_state['fa_empresa'] = None
    if 'fa_banco' not in st.session_state:
        st.session_state['fa_banco'] = None
    if 'fa_contrato' not in st.session_state:
        st.session_state['fa_contrato'] = None
    if 'fa_data_pagamento_ini' not in st.session_state:
        st.session_state['fa_data_pagamento_ini'] = None
    if 'fa_data_pagamento_fim' not in st.session_state:
        st.session_state['fa_data_pagamento_fim'] = None

    # inicializar session_states dos widgets a partir dos filtros salvos
    # (o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado)
    if 'fa_empresa_input' not in st.session_state:
        st.session_state['fa_empresa_input'] = st.session_state['fa_empresa'] or ''
    if 'fa_banco_input' not in st.session_state:
        st.session_state['fa_banco_input'] = st.session_state['fa_banco'] or ''
    if 'fa_contrato_input' not in st.session_state:
        st.session_state['fa_contrato_input'] = st.session_state['fa_contrato'] or ''
    if 'fa_data_pagamento_ini_input' not in st.session_state:
        st.session_state['fa_data_pagamento_ini_input'] = st.session_state['fa_data_pagamento_ini']
    if 'fa_data_pagamento_fim_input' not in st.session_state:
        st.session_state['fa_data_pagamento_fim_input'] = st.session_state['fa_data_pagamento_fim']

    # lista de filtros
    with st.form('antecipacoes_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            empresa = st.text_input('Empresa', key='fa_empresa_input')
            banco = st.text_input('Banco', key='fa_banco_input')
            contrato = st.text_input('Contrato', key='fa_contrato_input')
            data_pagamento_ini = st.date_input('Pagamento de', key='fa_data_pagamento_ini_input', format='DD/MM/YYYY')
            data_pagamento_fim = st.date_input('Pagamento até', key='fa_data_pagamento_fim_input', format='DD/MM/YYYY')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fa_empresa'] = empresa if empresa else None
            st.session_state['fa_banco'] = banco if banco else None
            st.session_state['fa_contrato'] = contrato if contrato else None
            st.session_state['fa_data_pagamento_ini'] = data_pagamento_ini
            st.session_state['fa_data_pagamento_fim'] = data_pagamento_fim

    # listando antecipações com filtros
    df_antecipacoes = listar_antecipacoes(
        empresa=st.session_state.get('fa_empresa'),
        banco=st.session_state.get('fa_banco'),
        contrato=st.session_state.get('fa_contrato'),
        data_pagamento_ini=st.session_state.get('fa_data_pagamento_ini'),
        data_pagamento_fim=st.session_state.get('fa_data_pagamento_fim')
    )

    if df_antecipacoes.empty:
        st.warning('Nenhuma antecipação encontrada com os filtros aplicados.')
        return

    # resumo calculado antes da formatação (valores ainda numéricos)
    resumo = resumir_antecipacoes(df_antecipacoes)

    # definindo formato
    df_antecipacoes['valor_pago'] = df_antecipacoes['valor_pago'].map(transformar_float_em_str)

    # inclusão da opção de seleção
    df_antecipacoes.insert(0, 'sel', False)

    # visualização do dataframe
    df_visual = st.data_editor(
        df_antecipacoes,
        width='content',
        hide_index=True,
        column_config={
            'sel': st.column_config.CheckboxColumn('', default=False),
            'data_pagamento': st.column_config.DateColumn(format='DD/MM/YYYY'),
        }
    )

    # resumo de valores
    st.caption(
        f"**Empresas:** {resumo['empresas']}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Bancos:** {resumo['bancos']}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Contratos:** {resumo['contratos']}&nbsp;&nbsp;|&nbsp;&nbsp;"
        f"**Total pago:** R$ {transformar_float_em_str(resumo['valor_pago'])}",
        unsafe_allow_html=True
    )

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
