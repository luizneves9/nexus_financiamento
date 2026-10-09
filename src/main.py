import streamlit as st
from pathlib import Path
from services.login import usuario_logado, renovar_sessao, sair
from views.login import tela_login
from views.components.botao_principal import estilo_botao_principal

LOGO = Path(__file__).parent / 'assets' / 'logo_nexus.svg'
ICONE = Path(__file__).parent / 'assets' / 'logo_nexus_icone.svg'

st.set_page_config(
    page_title='Sistema Nexus',
    page_icon=str(ICONE),
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Get help': None,
        'Report a bug': None,
        'About': '**Sistema Nexus** · Grupo GBS  \n'
                 'Sistema de gestão do financiamento de veículos da empresa.  \n'
                 'Dúvidas ou sugestões: fale com o administrador do sistema.'
    }
)

# CSS geral do sistema (aplicado depois do login, em toda execução)
ESTILO_GERAL = '''
    <style>
        /* logo do sidebar maior que o limite do st.logo (32 px), para o "SISTEMA" ficar legível */
        [data-testid="stSidebarLogo"] { height: 3rem; max-width: 100%; }

        /* ícone dos grupos alinhado ao ícone das páginas sem grupo (mesmo recuo interno dos links) */
        [data-testid="stNavSectionHeader"] { padding-left: 0.5rem; }

        /* recuo das páginas dentro dos grupos (não use espaços invisíveis no título: aparecem na aba do navegador) */
        [data-testid="stSidebarNavItems"] > :has([data-testid="stNavSectionHeader"]) [data-testid="stSidebarNavLink"] {
            padding-left: 2rem !important;
        }

        /* interações em índigo: ao passar o mouse, borda e fundo leve; vale nos temas claro e escuro */
        [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"],
        [data-testid="stPageLink-NavLink"],
        [data-testid="stSidebarNavLink"] { transition: border-color 0.15s, background-color 0.15s; }
        [data-testid="stBaseButton-secondary"]:hover, [data-testid="stBaseButton-secondaryFormSubmit"]:hover,
        [data-testid="stPageLink-NavLink"]:hover {
            border-color: #6366F1 !important;
            background-color: rgba(99, 102, 241, 0.08) !important;
            color: inherit !important;
        }
        [data-testid="stSidebarNavLink"]:hover { background-color: rgba(99, 102, 241, 0.10) !important; }

        /* campos (texto, data, listas): borda índigo no hover e em uso; cobre o Streamlit 1.57 (BaseWeb)
           e o 1.63 (componentes próprios, sem data-baseweb) */
        :is([data-testid="stTextInput"], [data-testid="stDateInput"], [data-testid="stTimeInput"])
            :is([data-testid="stTextInputRootElement"], [data-testid="stDateInputField"], [data-baseweb="input"]):is(:hover, :focus-within, [data-hovered], [data-focus-within]),
        [data-testid="stTextArea"]
            :is([data-testid="stTextAreaRootElement"], [data-baseweb="textarea"]):is(:hover, :focus-within),
        :is([data-testid="stSelectbox"], [data-testid="stMultiSelect"])
            :is([data-baseweb="select"] > div, .react-aria-Group, [role="group"]):is(:hover, :focus-within, [data-hovered], [data-focus-within]) {
            border-color: #6366F1 !important;
        }
        /* campo de número: borda do campo e botões − e + */
        [data-testid="stNumberInputContainer"]:is(:hover, :focus-within, .focused) { border-color: #6366F1 !important; }
        [data-testid="stNumberInputStepDown"]:hover:enabled, [data-testid="stNumberInputStepDown"]:focus:enabled,
        [data-testid="stNumberInputStepUp"]:hover:enabled, [data-testid="stNumberInputStepUp"]:focus:enabled {
            background-color: #6366F1 !important;
            color: #FFFFFF !important;
        }

        /* menos espaço acima do conteúdo; barra do topo transparente para não cobrir o título */
        [data-testid="stMainBlockContainer"] { padding-top: 3rem; }
        [data-testid="stHeader"] { background: transparent; }

        /* rodapé fixo no fim do sidebar (container com key='sb_rodape'), mesmo com o menu rolando */
        section[data-testid="stSidebar"] { will-change: transform; }
        section[data-testid="stSidebar"] *:has(.st-key-sb_rodape) { background-color: inherit; }
        .st-key-sb_rodape {
            position: fixed; left: 0; right: 0; bottom: 0; z-index: 100;
            background-color: inherit;
            padding: 0.75rem 1.5rem 1rem;
            border-top: 1px solid rgba(128, 128, 128, 0.25);
        }
        [data-testid="stSidebarContent"] { padding-bottom: 7rem; }
    </style>
'''

# fecha os grupos do menu no início da sessão, menos o da página atual
# (o "Sair" recarrega o navegador e abre uma nova sessão, então o menu é recolhido de novo no próximo login)
SCRIPT_RECOLHER_MENU = '''
    <script>
    (function () {
        let tentativas = 0;
        const recolher = () => {
            const titulos = document.querySelectorAll('[data-testid="stNavSectionHeader"]');
            if (!titulos.length) { if (tentativas++ < 25) setTimeout(recolher, 200); return; }
            titulos.forEach((titulo) => {
                const grupo = titulo.parentElement;
                const aberto = grupo.querySelector('[data-testid="stSidebarNavLink"]');
                const atual = grupo.querySelector('[data-testid="stSidebarNavLink"][aria-current="page"]');
                if (aberto && !atual) titulo.click();
            });
        };
        recolher();
    })();
    </script>
'''

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

    # identidade visual: logo no menu lateral, CSS geral e botão principal
    st.logo(str(LOGO), icon_image=str(ICONE), size='large')
    st.html(ESTILO_GERAL)
    estilo_botao_principal()

    # usuário e Sair fixos no fim do menu lateral
    with st.sidebar:
        with st.container(key='sb_rodape'):
            st.caption(f'Usuário: **{usuario}**')
            st.button('Sair', use_container_width=True, on_click=sair)

    pages = {
        ':material/request_quote: Operacional': [
            st.Page('views/contracts.py', title='Contratos'),
            st.Page('views/include_antecipation.py', title='Antecipação')
        ],
        ':material/folder_open: Cadastros': [
            st.Page('views/empresas.py', title='Empresas'),
            st.Page('views/bancos.py', title='Bancos'),
            st.Page('views/fornecedor.py', title='Fornecedor'),
        ],
        ':material/bar_chart: Relatórios': [
            st.Page('views/relatorio_projecao_pagamentos.py', title='Projeção de Pagamentos'),
            st.Page('views/relatorio_endividamento.py', title='Endividamento')
        ]
    }

    pg = st.navigation(pages)

    if not st.session_state.get('menu_recolhido'):
        st.session_state['menu_recolhido'] = True
        st.html(SCRIPT_RECOLHER_MENU, unsafe_allow_javascript=True)

    pg.run()

if __name__ == '__main__':
    main()
