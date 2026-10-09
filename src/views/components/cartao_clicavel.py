import streamlit as st

def estilo_cartao_clicavel(prefixo):
    '''Torna clicável o cartão inteiro dos containers com key '<prefixo><algo>' (st.container(border=True, key=...)).

    O st.page_link ou st.button do cartão ganha uma camada invisível (::after) que cobre o cartão: clicar em
    qualquer ponto aciona o link ou o botão. O cartão deve ter UM ÚNICO link ou botão.
    '''

    cartao = f'[class*="st-key-{prefixo}"]'
    st.html(f'''
        <style>
            {cartao} {{ position: relative; cursor: pointer; transition: border-color 0.15s, background-color 0.15s; }}
            {cartao} * {{ position: static !important; }}
            {cartao} a[data-testid="stPageLink-NavLink"]::after,
            {cartao} button[data-testid^="stBaseButton"]::after {{
                content: ""; position: absolute; inset: 0; z-index: 1;
            }}
            {cartao}:hover {{
                border-color: #6366F1 !important;
                background-color: rgba(99, 102, 241, 0.08);
            }}
        </style>
    ''')
