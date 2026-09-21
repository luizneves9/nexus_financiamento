import streamlit as st
from datetime import datetime
from services.liquidacao_antecipacao import (
	obter_dados_contrato,
	calcular_saldo_devedor,
	registrar_antecipacao
)
from tools.funcoes import transformar_float_em_str

def formatar_data(data):
	'''Formata data para exibição.'''
	if data is None:
		return '-'
	return data.strftime('%d/%m/%Y')

def formatar_valor(valor):
	'''Formata valor para exibição.'''
	if valor is None:
		return '-'
	return transformar_float_em_str(valor)

def formatar_selic(valor):
	'''Formata valor da Selic com 6 casas decimais (formato brasileiro).'''
	if valor is None:
		return '-'
	return f'{valor:,.6f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

@st.dialog('Antecipação / Liquidação de Contrato', width='medium', dismissible=False)
def modal_liquidacao_antecipacao(linha_contrato):
	'''Modal para registro de antecipação ou liquidação de contrato.'''

	# Obter dados do contrato
	id_contrato = int(linha_contrato['Id'])
	dados_contrato = obter_dados_contrato(id_contrato)

	if dados_contrato is None:
		st.error('Não foi possível carregar os dados do contrato.')
		return

	# Inicializar session_state para o modal
	if 'la_id_contrato' not in st.session_state:
		st.session_state['la_id_contrato'] = id_contrato
	if 'la_saldo_devedor' not in st.session_state:
		st.session_state['la_saldo_devedor'] = None
	if 'la_data_selic' not in st.session_state:
		st.session_state['la_data_selic'] = None
	if 'la_valor_selic' not in st.session_state:
		st.session_state['la_valor_selic'] = None
	if 'la_data_pagamento' not in st.session_state:
		st.session_state['la_data_pagamento'] = None
	if 'la_tipo_lancamento' not in st.session_state:
		st.session_state['la_tipo_lancamento'] = 'ANTECIPACAO'
	if 'la_valor_pago' not in st.session_state:
		st.session_state['la_valor_pago'] = 0.00
	if 'la_data_tesouraria' not in st.session_state:
		st.session_state['la_data_tesouraria'] = None
	if 'la_data_compensacao' not in st.session_state:
		st.session_state['la_data_compensacao'] = None

	# Seção de informações do contrato (somente leitura)
	st.markdown('**Informações do Contrato**')
	c1, c2, c3, c4 = st.columns([0.5, 1.5, 1.5, 1.5])

	c1.text_input('ID', value=str(dados_contrato['id']), disabled=True)
	c2.text_input('Número do Contrato', value=dados_contrato['numero_contrato'], disabled=True)
	c3.text_input('Empresa', value=dados_contrato['empresa'], disabled=True)
	c4.text_input('Banco', value=dados_contrato['banco'], disabled=True)

	c5, c6, c7 = st.columns([1.5, 1.5, 1.5])

	c5.text_input('Valor Financiado', value=formatar_valor(dados_contrato['valor_financiado']), disabled=True)
	c6.text_input('Data Emissão', value=formatar_data(dados_contrato['data_emissao']), disabled=True)
	c7.text_input('Data Vencimento', value=formatar_data(dados_contrato['data_ultima_parcela']), disabled=True)

	# Data de pagamento + botão para rodar o cálculo (identificar parcela, Selic, saldo devedor)
	c8, c9 = st.columns([2, 1], vertical_alignment='bottom')

	c8.date_input(
		'Data de Pagamento',
		format='DD/MM/YYYY',
		key='la_data_pagamento'
	)

	if c9.button('Calcular Saldo Devedor', use_container_width=True):
		if st.session_state['la_data_pagamento'] is None:
			st.session_state['mensagem_erro'] = 'Informe a data de pagamento antes de calcular.'
		else:
			resultado = calcular_saldo_devedor(id_contrato, st.session_state['la_data_pagamento'])
			if resultado is not None:
				st.session_state['la_saldo_devedor'] = resultado['saldo_devedor']
				st.session_state['la_data_selic'] = resultado['data_selic']
				st.session_state['la_valor_selic'] = resultado['valor_selic']

	c10, c11, c12 = st.columns([1.5, 1.5, 1.5])

	saldo_display = formatar_valor(st.session_state['la_saldo_devedor']) if isinstance(st.session_state['la_saldo_devedor'], (int, float)) else '-'
	data_selic_display = formatar_data(st.session_state['la_data_selic']) if st.session_state['la_data_selic'] else '-'
	valor_selic_display = formatar_selic(st.session_state['la_valor_selic']) if st.session_state['la_valor_selic'] else '-'

	c10.text_input('Saldo Devedor', value=saldo_display, disabled=True)
	c11.text_input('Data Selic', value=data_selic_display, disabled=True)
	c12.text_input('Valor Selic', value=valor_selic_display, disabled=True)

	st.divider()

	# Seção de operação (editável)
	st.markdown('**Dados da Operação**')

	c_op1, c_op2 = st.columns([1.5, 1.5])

	c_op1.selectbox(
		'Tipo de Lançamento',
		options=['ANTECIPACAO', 'QUITACAO'],
		key='la_tipo_lancamento'
	)

	c_op2.number_input(
		'Valor do Boleto',
		min_value=0.00,
		step=0.01,
		key='la_valor_pago'
	)

	c13, c14 = st.columns([1.5, 1.5])

	c13.date_input(
		'Data Tesouraria',
		format='DD/MM/YYYY',
		key='la_data_tesouraria'
	)

	c14.date_input(
		'Data Compensação',
		format='DD/MM/YYYY',
		key='la_data_compensacao'
	)

	st.divider()

	# Botões de ação
	col_confirmar, col_cancelar = st.columns(2)

	with col_confirmar:
		if st.button('Confirmar', type='primary', use_container_width=True):
			registrar_antecipacao(st.session_state)

	with col_cancelar:
		if st.button('Cancelar', use_container_width=True):
			# Limpar session_state
			campos_limpar = [
				'la_id_contrato',
				'la_saldo_devedor',
				'la_data_selic',
				'la_valor_selic',
				'la_data_pagamento',
				'la_tipo_lancamento',
				'la_valor_pago',
				'la_data_tesouraria',
				'la_data_compensacao'
			]
			for campo in campos_limpar:
				st.session_state.pop(campo, None)
			st.rerun()

	# Notificações
	if 'mensagem_sucesso' in st.session_state:
		st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')
		st.rerun()

	if 'mensagem_erro' in st.session_state:
		st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')
