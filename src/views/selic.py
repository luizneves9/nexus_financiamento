import streamlit as st
from services.selic import listar_selic, importar_selic
from views.components.cabecalho import cabecalho

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Selic', 'Fator Selic (UM143) importado do BNDES.', 'folder_open')

    # inicializar session_states dos filtros (FS = Filtro SELIC)
    if 'fs_data_ini' not in st.session_state:
        st.session_state['fs_data_ini'] = None
    if 'fs_data_fim' not in st.session_state:
        st.session_state['fs_data_fim'] = None

    # inicializar session_states dos widgets a partir dos filtros salvos
    # (o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado)
    if 'fs_data_ini_input' not in st.session_state:
        st.session_state['fs_data_ini_input'] = st.session_state['fs_data_ini']
    if 'fs_data_fim_input' not in st.session_state:
        st.session_state['fs_data_fim_input'] = st.session_state['fs_data_fim']

    # lista de filtros
    with st.form('selic_filtro'):
        with st.container(horizontal=True, vertical_alignment='bottom'):
            data_ini = st.date_input('Data de', key='fs_data_ini_input', format='DD/MM/YYYY')
            data_fim = st.date_input('Data até', key='fs_data_fim_input', format='DD/MM/YYYY')
            submitido = st.form_submit_button('Filtrar', use_container_width=True)

        if submitido:
            st.session_state['fs_data_ini'] = data_ini
            st.session_state['fs_data_fim'] = data_fim

    # importação da série do BNDES (só datas posteriores à última gravada)
    with st.container(horizontal=True):
        if st.button('Atualizar Selic (BNDES)'):
            with st.spinner('Baixando a SELIC do BNDES e recalculando os contratos...'):
                importar_selic()

    # listando SELIC com filtros
    with st.spinner('Consultando SELIC...'):
        df_selic = listar_selic(st.session_state.get('fs_data_ini'), st.session_state.get('fs_data_fim'))

    if df_selic.empty:
        st.warning('Nenhum valor de SELIC encontrado com os filtros aplicados.')

    else:
        # resumo calculado antes da formatação
        primeira, ultima, registros = df_selic['data'].min(), df_selic['data'].max(), len(df_selic)

        # definindo formato (6 casas, formato brasileiro)
        df_selic['valor'] = df_selic['valor'].map(
            lambda v: f'{v:,.6f}'.replace(',', 'v').replace('.', ',').replace('v', '.') if v is not None and v == v else None)

        # inclusão da opção de seleção
        df_selic.insert(0, 'sel', False)

        # visualização do dataframe
        st.data_editor(
            df_selic,
            width='content',
            hide_index=True,
            disabled=True,
            column_config={
                'sel': st.column_config.CheckboxColumn('', default=False),
                'id': 'Id',
                'data': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
                'valor': 'Valor',
            }
        )

        # resumo
        st.caption(
            f"**Registros:** {registros}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Primeira data:** {primeira:%d/%m/%Y}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Última data:** {ultima:%d/%m/%Y}",
            unsafe_allow_html=True
        )

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()
