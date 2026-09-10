import streamlit as st

st.set_page_config(
    page_title='NEXUS | Financiamento',
    layout='wide'
)

def main():
    pages = {
        'Operacional': [
            st.Page('views/contracts.py', title='Contratos'),
            st.Page('views/include_antecipation.py', title='Antecipação')
        ],
        'Cadastros': [
            st.Page('views/empresas.py', title='Empresas')
        ]
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == '__main__':
    main()