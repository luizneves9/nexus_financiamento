import streamlit as st
from services.empresas import listar_empresas
from views.components.cabecalho import cabecalho

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Gestão de Empresas', 'Lista das empresas cadastradas no sistema.', 'folder_open')

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