import streamlit as st
from services.empresas import listar_empresas

def main():

    # definindo o título da página
    st.markdown('''
        <h2 style='margin-bottom: 0px;'>Gestão de Empresas</h2>
        <p style='margin-top: -15px; color: #666; font-style: italic;'>
            Lista das empresas cadastradas no sistema.
        </p>
        ''',
        unsafe_allow_html=True
    )

    # listando contratos
    df_empresas = listar_empresas()

    # inclusão da opção de seleção
    df_empresas.insert(0, 'sel', False)

    # visualização do dataframe
    df_visual = st.data_editor(
        df_empresas,
        width='content',
        hide_index=True,
        column_config={
            'sel': st.column_config.CheckboxColumn('', default=False)
        }
    )
    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')

if __name__ == '__main__':
    main()