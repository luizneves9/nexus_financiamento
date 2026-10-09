import streamlit as st
from services.fornecedor import listar_fornecedores
from views.components.cabecalho import cabecalho

def main():

    # cabeçalho padrão da tela (ícone do grupo no menu)
    cabecalho('Gestão de Fornecedores', 'Lista dos fornecedores cadastrados no sistema.', 'folder_open')

    # listando contratos
    df_fornecedores = listar_fornecedores()

    # inclusão da opção de seleção
    df_fornecedores.insert(0, 'sel', False)

    # visualização do dataframe
    df_visual = st.data_editor(
        df_fornecedores,
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