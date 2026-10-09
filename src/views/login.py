import streamlit as st
from pathlib import Path
from services.login import autenticar, cadastrar_senha, cancelar_primeiro_acesso, apagar_cookie_sessao
from views.components.botao_principal import estilo_botao_principal

LOGO = Path(__file__).parent.parent / 'assets' / 'logo_nexus.svg'

def tela_login():
    '''Tela de login exibida antes da navegação do sistema.'''

    # apaga o cookie do navegador caso o usuário tenha acabado de sair
    apagar_cookie_sessao()

    # o CSS geral só vale depois do login: aplica aqui o estilo do botão principal
    estilo_botao_principal()

    _, centro, _ = st.columns([1, 1, 1])

    with centro:
        # logo centralizada no lugar do título
        with st.container(horizontal_alignment='center'):
            st.image(str(LOGO), width=280)

        primeiro_acesso = st.session_state.get('auth_primeiro_acesso')

        # primeiro acesso: cadastro da senha
        if primeiro_acesso:
            st.info(f"Primeiro acesso de **{primeiro_acesso['usuario']}**. Cadastre sua senha.")

            with st.form('cadastrar_senha'):
                nova_senha = st.text_input('Nova senha', type='password')
                confirmacao = st.text_input('Confirmar senha', type='password')
                cadastrar = st.form_submit_button('Cadastrar senha', type='primary', use_container_width=True)

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
                entrar = st.form_submit_button('Entrar', type='primary', use_container_width=True)

            if entrar:
                if autenticar(usuario.strip(), senha):
                    st.rerun()
                # primeiro acesso identificado: exibe o cadastro de senha
                if st.session_state.get('auth_primeiro_acesso'):
                    st.rerun()

            with st.container(horizontal_alignment='center'):
                st.caption('Esqueceu a senha ou ainda não tem acesso? Fale com o administrador do sistema.')

    if 'mensagem_login' in st.session_state:
        st.toast(st.session_state.pop('mensagem_login'), icon='⚠️')
