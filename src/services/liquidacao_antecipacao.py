import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from database.connection import ConexaoBancoSQL
from queries.queries_antecipacao import (
	SELECT_DADOS_CONTRATO,
	SELECT_PARCELA_SALDO_DEVEDOR,
	SELECT_SELIC,
	VERIFICAR_QUITACAO_EXISTENTE,
	INSERIR_ANTECIPACAO
)
from repositories.include_antecipation import registrar_contrato

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def obter_dados_contrato(id_contrato):
	'''Obtém os dados essenciais do contrato para o modal.'''
	try:
		with engine.connect() as conn:
			query = text(SELECT_DADOS_CONTRATO)
			resultado = pd.read_sql(
				query,
				conn,
				params={'id_contrato': id_contrato}
			)
			if resultado.empty:
				return None
			return resultado.iloc[0].to_dict()
	except Exception as e:
		st.session_state['mensagem_erro'] = f'Erro ao buscar dados do contrato: {str(e)}'
		return None

def calcular_saldo_devedor(id_contrato, data_pagamento):
	'''Calcula o saldo devedor baseado na data de pagamento fornecida.'''
	try:
		with engine.connect() as conn:
			# Buscar parcela: primeira com vencimento >= data de pagamento,
			# ou a mais recente do contrato caso não haja parcela futura
			query_parcela = text(SELECT_PARCELA_SALDO_DEVEDOR)
			resultado_parcela = pd.read_sql(
				query_parcela,
				conn,
				params={'id_contrato': id_contrato, 'data_pagamento': data_pagamento}
			)

			if resultado_parcela.empty:
				st.session_state['mensagem_erro'] = (
					'Nenhuma parcela encontrada para este contrato. '
					'A funcionalidade atende apenas contratos do tipo BNDES FINAME SELIC.'
				)
				return None

			saldo_devedor = float(resultado_parcela.iloc[0]['saldo_devedor'])

			# Buscar Selic: exata/próxima disponível, ou a mais recente do banco
			query_selic = text(SELECT_SELIC)
			resultado_selic = pd.read_sql(query_selic, conn, params={'data_pagamento': data_pagamento})

			if resultado_selic.empty:
				st.session_state['mensagem_erro'] = 'Nenhuma Selic cadastrada no banco de dados.'
				return None

			valor_selic = float(resultado_selic.iloc[0]['valor'])
			data_selic = resultado_selic.iloc[0]['data']

			# Calcular saldo devedor em moeda (multiplicado pela Selic)
			saldo_em_moeda = round(saldo_devedor * valor_selic, 2)

			return {
				'saldo_devedor': saldo_em_moeda,
				'data_selic': data_selic,
				'valor_selic': valor_selic
			}

	except Exception as e:
		st.session_state['mensagem_erro'] = f'Erro ao calcular saldo devedor: {str(e)}'
		return None

def verificar_quitacao_existente(id_contrato):
	'''Verifica se já existe uma quitação registrada para este contrato.'''
	try:
		with engine.connect() as conn:
			query = text(VERIFICAR_QUITACAO_EXISTENTE)
			resultado = pd.read_sql(query, conn, params={'id_contrato': id_contrato})
			return resultado.iloc[0]['count'] > 0
	except Exception:
		return False

def validar_dados_antecipacao(id_contrato, tipo_lancamento, valor_pago,
							   data_pagamento, data_tesouraria, data_compensacao):
	'''Realiza validações dos dados antes da inserção.'''

	# Verificar se é quitação e se já existe uma registrada
	if tipo_lancamento == 'QUITACAO' and verificar_quitacao_existente(id_contrato):
		return False, 'Já existe uma quitação registrada para este contrato.'

	# Validar valor do boleto > 0
	if valor_pago <= 0:
		return False, 'O valor do boleto deve ser maior que zero.'

	# Validar datas: DATA COMPENSAÇÃO >= TESOURARIA >= PAGAMENTO
	if data_pagamento > data_tesouraria:
		return False, 'A data de pagamento não pode ser maior que a data de tesouraria.'

	if data_tesouraria > data_compensacao:
		return False, 'A data de tesouraria não pode ser maior que a data de compensação.'

	return True, None

def registrar_antecipacao(session_state):
	'''Registra a antecipação/liquidação no banco de dados.'''

	# Validar se todos os campos obrigatórios foram preenchidos
	campos_obrigatorios = [
		'la_id_contrato',
		'la_data_pagamento',
		'la_tipo_lancamento',
		'la_valor_pago',
		'la_data_tesouraria',
		'la_data_compensacao'
	]

	campos_nao_preenchidos = []
	for campo in campos_obrigatorios:
		if campo not in session_state or session_state[campo] is None:
			campos_nao_preenchidos.append(campo.replace('la_', '').replace('_', ' ').title())

	if campos_nao_preenchidos:
		session_state['mensagem_erro'] = f'Preencha todos os campos obrigatórios! {", ".join(campos_nao_preenchidos)}'
		return

	# Validar dados
	valido, mensagem_erro = validar_dados_antecipacao(
		session_state['la_id_contrato'],
		session_state['la_tipo_lancamento'],
		session_state['la_valor_pago'],
		session_state['la_data_pagamento'],
		session_state['la_data_tesouraria'],
		session_state['la_data_compensacao']
	)

	if not valido:
		session_state['mensagem_erro'] = mensagem_erro
		return

	# Preparar parâmetros
	parametro = {
		'id_contrato': session_state['la_id_contrato'],
		'data_pagamento': session_state['la_data_pagamento'],
		'data_tesouraria': session_state['la_data_tesouraria'],
		'valor_pago': session_state['la_valor_pago'],
		'tipo_lancamento': session_state['la_tipo_lancamento'],
		'data_compensacao': session_state['la_data_compensacao']
	}

	query = text(INSERIR_ANTECIPACAO)

	# Inserir no banco de dados
	try:
		with engine.begin() as conn:
			registrar_contrato(query, conn, parametro)

		# Limpar session_state
		campos_para_limpar = campos_obrigatorios + [
			'la_saldo_devedor',
			'la_data_selic',
			'la_valor_selic'
		]
		for campo in campos_para_limpar:
			if campo in session_state:
				session_state.pop(campo, None)

		session_state['mensagem_sucesso'] = 'Antecipação/Liquidação registrada com sucesso!'
		st.rerun()

	except IntegrityError as e:
		if 'antecipacao_id_contrato_fkey' in str(e.orig):
			session_state['mensagem_erro'] = 'Contrato não encontrado.'
		else:
			session_state['mensagem_erro'] = 'Os dados violam uma regra de integridade.'
		st.rerun()
	except OperationalError:
		session_state['mensagem_erro'] = 'Não foi possível acessar o banco de dados.'
		st.rerun()
	except Exception as e:
		session_state['mensagem_erro'] = f'Erro ao registrar antecipação: {str(e)}'
		st.rerun()
