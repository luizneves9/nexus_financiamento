import pandas as pd
import streamlit as st
from services.consorcio import (PAGO, ler_csv_consorcio, resumir_substituicao, importar_consorcio, competencia_do_mes,
                                listar_consorciados)
from tools.funcoes import transformar_float_em_str

def limpar_importacao():
    '''Remove do session_state a leitura do arquivo guardada enquanto o modal está aberto.'''
    for chave in ('fco_imp_chave', 'fco_imp_leitura'):
        st.session_state.pop(chave, None)

@st.dialog('Importar consórcio', width='large', dismissible=False)
def modal_consorcio_importar(tipo, data_base_padrao):
    '''Modal de importação do CSV de consórcio (um arquivo por banco): pago ou a pagar.'''

    if tipo == PAGO:
        st.markdown('*Pagamentos registrados pela Data Pagamento, um arquivo por banco e consorciado. O arquivo pode trazer '
                    'só o mês ou o histórico completo: os pagamentos do banco e consorciado no período do arquivo são substituídos.*')
        competencia, consorciado = None, None
    else:
        st.markdown('*Parcelas a pagar das cotas contempladas, na posição da data base, um arquivo por banco e consorciado. '
                    'A importação substitui a foto do banco e consorciado nesta competência; os demais não mudam.*')
        with st.container(horizontal=True, vertical_alignment='bottom'):
            data_base = st.date_input('Data base', value=data_base_padrao, key='fco_imp_data_base', format='DD/MM/YYYY')
            consorciado = st.selectbox('Consorciado', listar_consorciados(), index=None, accept_new_options=True,
                                       placeholder='Selecione ou digite', key='fco_imp_consorciado')
        competencia = competencia_do_mes(data_base)
        st.caption(f'Competência gravada: **{competencia:%m/%Y}**')

    rotulo = 'CSV de consórcio pago' if tipo == PAGO else 'CSV de consórcio a pagar'
    arquivo = st.file_uploader(rotulo, type=['csv'], key=f'fco_imp_arquivo_{tipo}')

    if arquivo is not None:

        # lê o arquivo uma única vez (guardado no session_state enquanto o modal estiver aberto)
        chave_arquivo = f'{tipo}|{arquivo.name}|{arquivo.size}'
        if st.session_state.get('fco_imp_chave') != chave_arquivo:
            st.session_state['fco_imp_chave'] = chave_arquivo
            st.session_state['fco_imp_leitura'] = ler_csv_consorcio(arquivo, tipo)

        leitura = st.session_state['fco_imp_leitura']

        if leitura['erro']:
            st.error(leitura['erro'])

        else:
            # prévia do arquivo (valores numéricos só para exibição)
            df = pd.DataFrame(leitura['linhas'])
            for coluna in df.columns:
                if coluna.startswith('valor'):
                    df[coluna] = df[coluna].map(lambda v: float(v) if v is not None else None)

            st.dataframe(
                df,
                hide_index=True,
                column_config={
                    'banco': 'Banco',
                    'nome_consorciado': 'Consorciado',
                    'numero_proposta': 'Proposta',
                    'data_adesao': st.column_config.DateColumn('Adesão', format='DD/MM/YYYY'),
                    'id_cota': 'Cota',
                    'movimento': 'Movimento',
                    'data_pagamento': st.column_config.DateColumn('Data pagamento', format='DD/MM/YYYY'),
                    'valor_fundo_comum': st.column_config.NumberColumn('Fundo comum', format='localized'),
                    'valor_fundo_reserva': st.column_config.NumberColumn('Fundo reserva', format='localized'),
                    'valor_taxa_administracao': st.column_config.NumberColumn('Taxa adm.', format='localized'),
                    'valor_multa_juros': st.column_config.NumberColumn('Multa e juros', format='localized'),
                    'valor_outros': st.column_config.NumberColumn('Outros', format='localized'),
                    'valor_total': st.column_config.NumberColumn('Total', format='localized'),
                    'valor_parcela': st.column_config.NumberColumn('Valor parcela', format='localized'),
                    'data_emissao': st.column_config.DateColumn('Emissão', format='DD/MM/YYYY'),
                }
            )

            st.caption(
                f"**Banco:** {leitura['banco']}&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"**Consorciado:** {leitura['consorciado'] or consorciado or '(não informado)'}&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"**Linhas:** {len(leitura['linhas'])} (vazias descartadas: {leitura['descartadas']})&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"**Período:** {leitura['data_ini']:%d/%m/%Y} a {leitura['data_fim']:%d/%m/%Y}&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"**Total:** R\\$ {transformar_float_em_str(leitura['total'])}",
                unsafe_allow_html=True
            )

            # o que já está gravado e será substituído (a pagar: só depois de informar o consorciado)
            if tipo == PAGO or consorciado:
                substituido = resumir_substituicao(tipo, leitura, competencia, consorciado)
                if substituido['qtd']:
                    if tipo == PAGO:
                        st.warning(f"Serão substituídos {substituido['qtd']} pagamento(s) (R\\$ {transformar_float_em_str(substituido['total'])}) "
                                   f"do banco {leitura['banco']} / {leitura['consorciado']} entre "
                                   f"{leitura['data_ini']:%d/%m/%Y} e {leitura['data_fim']:%d/%m/%Y}.")
                    else:
                        st.warning(f"Serão substituídas {substituido['qtd']} parcela(s) a pagar (R\\$ {transformar_float_em_str(substituido['total'])}) "
                                   f"do banco {leitura['banco']} / {consorciado} na competência {competencia:%m/%Y}.")

            if st.button('Confirmar', type='primary', use_container_width=True):
                if tipo != PAGO and not consorciado:
                    st.error('Informe o consorciado do arquivo a pagar.')
                elif importar_consorcio(tipo, leitura, arquivo.name, competencia, consorciado):
                    limpar_importacao()
                    st.rerun()
                else:
                    st.error(st.session_state.pop('mensagem_erro', 'Erro ao importar o consórcio.'))

    if st.button('Cancelar', use_container_width=True):
        limpar_importacao()
        st.rerun()
