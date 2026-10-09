import streamlit as st

# botão principal (st.button / st.form_submit_button com type='primary'): discreto em repouso (fundo índigo
# translúcido, borda e texto índigo) e, ao passar o mouse, preenchido com o degradê do "NEXUS" da logo
# (#3B82F6 → #9333EA) e um brilho suave. Funciona nos temas claro e escuro e substitui o vermelho padrão.
ESTILO_BOTAO_PRINCIPAL = '''
    <style>
        [data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-primaryFormSubmit"] {
            background: rgba(99, 102, 241, 0.12) !important;
            border: 1px solid rgba(99, 102, 241, 0.55) !important;
            color: #6366F1 !important;
            font-weight: 600;
            letter-spacing: 0.02em;
            transition: background 0.2s, color 0.2s, box-shadow 0.2s, border-color 0.2s;
        }
        [data-testid="stBaseButton-primary"] p,
        [data-testid="stBaseButton-primaryFormSubmit"] p { color: inherit !important; }
        [data-testid="stBaseButton-primary"]:hover,
        [data-testid="stBaseButton-primaryFormSubmit"]:hover {
            background: linear-gradient(90deg, #3B82F6, #9333EA) !important;
            border-color: transparent !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 18px rgba(99, 102, 241, 0.45);
        }
        [data-testid="stBaseButton-primary"]:active,
        [data-testid="stBaseButton-primaryFormSubmit"]:active { filter: brightness(0.9); }
        [data-testid="stBaseButton-primary"]:disabled,
        [data-testid="stBaseButton-primaryFormSubmit"]:disabled { opacity: 0.5; box-shadow: none; }
    </style>
'''

def estilo_botao_principal():
    '''Aplica o estilo do botão principal na página (login e, pelo arquivo principal, todas as telas).'''
    st.html(ESTILO_BOTAO_PRINCIPAL)
