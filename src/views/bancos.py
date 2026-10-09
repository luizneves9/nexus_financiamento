import streamlit as st
from services.bancos import listar_bancos
from views.components.cabecalho import cabecalho

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Gestão de Bancos', 'Lista dos bancos cadastrados no sistema.', 'folder_open')

    # listando contratos
    df_bancos = listar_bancos()

    # inclusão da opção de seleção
    df_bancos.insert(0, 'sel', False)

    # visualização do dataframe
    df_visual = st.data_editor(
        df_bancos,
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