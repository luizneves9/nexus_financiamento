import streamlit as st
from services.login import autenticar, cadastrar_senha, cancelar_primeiro_acesso, apagar_cookie_sessao

def tela_login():
    '''Tela de login exibida antes da navegação do sistema.'''

    # apaga o cookie do navegador caso o usuário tenha acabado de sair
    apagar_cookie_sessao()

    _, centro, _ = st.columns([1, 1, 1])

    with centro:
        # definindo o título da página
        st.markdown('''
            <h2 style='margin-bottom: 0px;'>NEXUS</h2>
            <p style='margin-top: -15px; color: #666; font-style: italic;'>
                Gestão de contratos de financiamento.
            </p>
            ''',
            unsafe_allow_html=True
        )

        primeiro_acesso = st.session_state.get('auth_primeiro_acesso')

        # primeiro acesso: cadastro da senha
        if primeiro_acesso:
            st.info(f"Primeiro acesso de **{primeiro_acesso['usuario']}**. Cadastre sua senha.")

            with st.form('cadastrar_senha'):
                nova_senha = st.text_input('Nova senha', type='password')
                confirmacao = st.text_input('Confirmar senha', type='password')
                cadastrar = st.form_submit_button('Cadastrar senha', use_container_width=True)

            # texto clicável (sem formato de botão) para voltar ao login
            with st.container(horizontal_alignment='center'):
                st.button('Voltar/cancelar', type='tertiary', on_click=cancelar_primeiro_acesso)

            if cadastrar and cadastrar_senha(nova_senha, confirmacao):
                st.rerun()

        # login
        else:
            with st.form('login'):
                usuario = st.text_input('Usuário')
                senha = st.text_input('Senha', type='password')
                entrar = st.form_submit_button('Entrar', use_container_width=True)

            if entrar:
                if autenticar(usuario.strip(), senha):
                    st.rerun()
                # primeiro acesso identificado: exibe o cadastro de senha
                if st.session_state.get('auth_primeiro_acesso'):
                    st.rerun()

    if 'mensagem_login' in st.session_state:
        st.toast(st.session_state.pop('mensagem_login'), icon='⚠️')
