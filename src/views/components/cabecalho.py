import html
import streamlit as st

def cabecalho(titulo, subtitulo, icone):
    '''Cabeçalho padrão: ícone do grupo do menu (em roxo) + título e subtítulo em itálico.

    `icone`: nome do Material Symbol, o mesmo do grupo da tela no menu (ex.: 'account_balance').
    O subtítulo usa a cor do texto do tema com opacidade reduzida, legível nos temas claro e escuro.
    '''

    st.header(f':violet[:material/{icone}:] {titulo}', anchor=False)
    st.markdown(
        f"<p style='margin-top: -0.9rem; opacity: 0.7; font-style: italic;'>{html.escape(subtitulo)}</p>",
        unsafe_allow_html=True
    )
