import streamlit as st

st.set_page_config(
    page_title='NEXUS | Financiamento',
    layout='wide'
)

def main():
    pages = {
        'Operacional': [
            st.Page('views/contracts.py', title='Contratos'),
            st.Page('views/include_contract.py', title='Inclusão de Contrato'),
            st.Page('views/include_antecipation.py', title='Antecipação')
        ]
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == '__main__':
    main()