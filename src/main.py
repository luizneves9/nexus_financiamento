import streamlit as st
from services.login import usuario_logado, renovar_sessao, sair
from views.login import tela_login

st.set_page_config(
    page_title='NEXUS | Financiamento',
    layout='wide'
)

def main():
    # sem usuário logado, exibe somente a tela de login
    usuario = usuario_logado()
    # (a tela de login também passa pelo st.navigation, com menu oculto, para limpar as abas laterais)
    if not usuario:
        pg = st.navigation([st.Page(tela_login, title='Login')], position='hidden')
        pg.run()
        return

    # renova a permanência do login (30 min) enquanto o usuário usa o sistema
    renovar_sessao()

    with st.sidebar:
        st.caption(f'Usuário: **{usuario}**')
        st.button('Sair', use_container_width=True, on_click=sair)

    pages = {
        'Operacional': [
            st.Page('views/contracts.py', title='Contratos'),
            st.Page('views/include_antecipation.py', title='Antecipação')
        ],
        'Cadastros': [
            st.Page('views/empresas.py', title='Empresas'),
            st.Page('views/bancos.py', title='Bancos'),
            st.Page('views/fornecedor.py', title='Fornecedor'),
        ],
        'Relatórios': [
            st.Page('views/relatorio_projecao_pagamentos.py', title='Projeção de Pagamentos'),
            st.Page('views/relatorio_endividamento.py', title='Endividamento')
        ]
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == '__main__':
    main()