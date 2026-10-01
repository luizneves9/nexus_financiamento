import streamlit as st
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError
from database.connection import ConexaoBancoSQL
from queries.queries_gerais import INCLUIR_CONTRATO, SELECT_CONTRATOS
from queries.queries_contracts import (
    DELETE_CONTRATO,
    PROJETAR_CONTRATO_SELIC,
    PROJETAR_CONTRATO_TFC,
    SELECT_PROJECAO,
)
from repositories.include_antecipation import registrar_contrato, consultar_contratos
from repositories.contract import listar_projecao, interacao_database, listar_contratos as ler_contratos_banco
from views.components.modal_contracts_projecao import modal_projecao_valores
from tools.funcoes import transformar_float_em_str
from services.log import registrar_log, registrar_log_falha, CONTRATO_INCLUIR, CONTRATO_EXCLUIR

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

def incluir_contrato(session_state):
    '''Processo de inclusão de contrato, incluindo regras de negócios.'''

    # validando preenchimento das colunas
    campos_nao_preenchidos = []
    for key, val in session_state.items():
        if 'ic_' in key and (val is None or str(val) == ''):
            key = f'{key}'.replace('ic_', '').replace('_', ' ').title()
            campos_nao_preenchidos.append(key)

    if campos_nao_preenchidos:
        session_state['mensagem_erro'] = f'Preencha todos os campos! {', '.join(campos_nao_preenchidos)}'
        return

    # validando valores incluidos
    if session_state['ic_dt_bndes'] < session_state['ic_dt_emissao']:
        session_state['mensagem_erro'] = f'A data BNDES deve ser maior ou igual que a data de emissão.'
        return

    if session_state['ic_valor_financiado'] <= 0:
        session_state['mensagem_erro'] = f'O valor financiado deve ser maior que zero!'
        return

    if session_state['ic_taxa_juros_efetiva'] <= 0:
        session_state['mensagem_erro'] = f'O juros total deve ser maior que zero!'
        return

    if session_state['ic_prazo_total'] <= 0:
        session_state['mensagem_erro'] = f'O prazo total deve ser maior que zero!'
        return

    if session_state['ic_prazo_carencia'] <= 0:
        session_state['mensagem_erro'] = f'O prazo de carência deve ser maior que zero!'
        return

    if session_state['ic_prazo_final'] <= 0:
        session_state['mensagem_erro'] = f'O prazo final deve ser maior que zero!'
        return

    if session_state['ic_pagamento_carencia'] < 0:
        session_state['mensagem_erro'] = f'O pagamento de carência deve ser maior ou igual a zero!'
        return

    if session_state['ic_dt_primeiro_encargo'] <= session_state['ic_dt_emissao']:
        session_state['mensagem_erro'] = f'A data do primeiro encargo deve ser maior que a data de emissão do contrato!'
        return

    if session_state['ic_dt_primeiro_principal'] <= session_state['ic_dt_primeiro_encargo']:
        session_state['mensagem_erro'] = f'A data do primeiro principal deve ser maior que a data do primeiro encargo!'
        return

    if session_state['ic_dt_ultima_parcela'] <= session_state['ic_dt_primeiro_principal']:
        session_state['mensagem_erro'] = f'A data da última parcela deve ser maior que a data do primeiro principal!'
        return

    # definindo e ajustando parâmetros
    empresa_selecionada = session_state['df_lista_empresas'].loc[
        session_state['df_lista_empresas']['razao_social'] == session_state['ic_empresas'],
        'id'
    ]
    if empresa_selecionada.empty:
        session_state['mensagem_erro'] = 'A empresa selecionada não está disponível.'
        return

    banco_selecionado = session_state['df_lista_bancos'].loc[
        session_state['df_lista_bancos']['razao_social'] == session_state['ic_bancos'],
        'id'
    ]
    if banco_selecionado.empty:
        session_state['mensagem_erro'] = 'O banco selecionado não está disponível.'
        return

    id_empresa = int(empresa_selecionada.iloc[0])
    id_banco = int(banco_selecionado.iloc[0])
    debito_em_conta = True if session_state['ic_debito_cc'] == 'SIM' else False

    # definindo os parâmetros
    parametro = {
        'id_empresa': id_empresa,
        'id_banco': id_banco,
        'contrato': session_state['ic_numero_contrato'],
        'data_emissao': session_state['ic_dt_emissao'],
        'data_bndes': session_state['ic_dt_bndes'],
        'tipo': session_state['ic_tipo'],
        'valor': session_state['ic_valor_financiado'],
        'pos_fixado': session_state['ic_pos_fixado'],
        'custo_bndes': session_state['ic_custo_bndes'],
        'sobretaxa_bndes': session_state['ic_sobretaxa_bndes'],
        'juros_banco': session_state['ic_taxa_banco'],
        'juros_total': session_state['ic_taxa_juros_efetiva'],
        'prazo_total': session_state['ic_prazo_total'],
        'prazo_carencia': session_state['ic_prazo_carencia'],
        'prazo_final': session_state['ic_prazo_final'],
        'data_primeira_parcela_encargo': session_state['ic_dt_primeiro_encargo'],
        'data_primeira_parcela_prestacao': session_state['ic_dt_primeiro_principal'],
        'data_ultima_parcela': session_state['ic_dt_ultima_parcela'],
        'debito_conta_corrente': debito_em_conta,
        'carencia_pagamento': session_state['ic_pagamento_carencia'],
        'registro_cobranca': session_state['ic_registro_cobranca']
    }

    # definindo a query
    query = text(INCLUIR_CONTRATO)

    # dados do contrato para o log de auditoria
    detalhes_log = {
        'numero_contrato': parametro['contrato'],
        'empresa': session_state['ic_empresas'],
        'banco': session_state['ic_bancos'],
        'tipo_contrato': parametro['tipo'],
        'valor_financiado': parametro['valor'],
        'data_emissao': parametro['data_emissao']
    }

    # conexão com o banco de dados (contrato e log na mesma transação)
    try:
        with engine.begin() as conn:
            id_contrato = registrar_contrato(query, conn, parametro).scalar_one()
            registrar_log(CONTRATO_INCLUIR, 'contratos', id_contrato, detalhes=detalhes_log, conn=conn)
        st.session_state['mensagem_sucesso'] = 'Contrato incluído com sucesso!'
        st.rerun()
    except IntegrityError as e:
        if 'contratos_numero_contrato_key' in str(e.orig):
            st.session_state['mensagem_erro'] = 'O número do contrato já está cadastrado.'
        else:
            st.session_state['mensagem_erro'] = 'Os dados do contrato violam uma regra de integridade.'
        registrar_log_falha(CONTRATO_INCLUIR, e.orig, 'contratos', detalhes=detalhes_log)
        st.rerun()
    except OperationalError as e:
        st.session_state['mensagem_erro'] = 'Não foi possível acessar o banco de dados.'
        registrar_log_falha(CONTRATO_INCLUIR, e.orig, 'contratos', detalhes=detalhes_log)
        st.rerun()
    except Exception as e:
        st.session_state['mensagem_erro'] = 'Não foi possível incluir o contrato.'
        registrar_log_falha(CONTRATO_INCLUIR, e, 'contratos', detalhes=detalhes_log)
        st.rerun()

def projetar_contrato(session_state):
    '''Calcula a projeção temporária sem persistir o contrato.'''

    campos_obrigatorios = [
        'ic_dt_emissao',
        'ic_dt_bndes',
        'ic_valor_financiado',
        'ic_taxa_juros_efetiva',
        'ic_prazo_carencia',
        'ic_prazo_final',
        'ic_pagamento_carencia',
        'ic_registro_cobranca',
        'ic_tipo',
    ]
    campos_nao_preenchidos = [
        campo for campo in campos_obrigatorios
        if session_state.get(campo) is None or str(session_state.get(campo)) == ''
    ]

    if campos_nao_preenchidos:
        session_state['mensagem_erro'] = 'Preencha os campos necessários para projetar.'
        return pd.DataFrame()

    if session_state['ic_valor_financiado'] <= 0:
        session_state['mensagem_erro'] = 'O valor financiado deve ser maior que zero!'
        return pd.DataFrame()

    if session_state['ic_taxa_juros_efetiva'] <= 0:
        session_state['mensagem_erro'] = 'A taxa de juros efetiva deve ser maior que zero!'
        return pd.DataFrame()

    if session_state['ic_prazo_carencia'] <= 0 or session_state['ic_prazo_final'] <= 0:
        session_state['mensagem_erro'] = 'Os prazos devem ser maiores que zero!'
        return pd.DataFrame()

    if session_state['ic_dt_bndes'] < session_state['ic_dt_emissao']:
        session_state['mensagem_erro'] = 'A data BNDES deve ser maior ou igual à data de emissão.'
        return pd.DataFrame()

    parametros = {
        'data_emissao': session_state['ic_dt_emissao'],
        'data_bndes': session_state['ic_dt_bndes'],
        'valor_financiado': session_state['ic_valor_financiado'],
        'taxa_juros_efetiva': session_state['ic_taxa_juros_efetiva'],
        'prazo_carencia': session_state['ic_prazo_carencia'],
        'prazo_final': session_state['ic_prazo_final'],
        'carencia_pagamento': session_state['ic_pagamento_carencia'],
        'registro_cobranca': session_state['ic_registro_cobranca'],
    }

    tipo_contrato = session_state['ic_tipo']
    if tipo_contrato == 'BNDES FINAME SELIC':
        query = PROJETAR_CONTRATO_SELIC
    elif tipo_contrato == 'BNDES FINAME TFC':
        query = PROJETAR_CONTRATO_TFC
        parametros.pop('registro_cobranca')
    else:
        session_state['mensagem_erro'] = f'Tipo de contrato não suportado: {tipo_contrato}'
        return pd.DataFrame()

    try:
        with engine.begin() as conn:
            return listar_projecao(text(query), conn, parametros)
    except OperationalError:
        session_state['mensagem_erro'] = 'Não foi possível acessar o banco para calcular a projeção.'
        return pd.DataFrame()
    except Exception:
        session_state['mensagem_erro'] = 'Não foi possível calcular a projeção.'
        return pd.DataFrame()

def listar_contratos(empresa=None, banco=None, contrato=None):
    '''Função definida para listar contratos registrados no banco de dados com filtros opcionais.'''

    df = pd.DataFrame()
    parametros = {
        'empresa': f"%{empresa}%" if empresa else None,
        'banco': f"%{banco}%" if banco else None,
        'contrato': f"%{contrato}%" if contrato else None
    }

    try:
        with engine.begin() as conn:
            df = ler_contratos_banco(text(SELECT_CONTRATOS), conn, parametros)
    except:
        pass

    return df

def visualizar_projecao(linha_selecionada):
    '''Visualização da projeção referente a um contrato.'''

    # validando quantidade selecionada (deve ser um)
    if len(linha_selecionada) != 1:
        st.session_state['mensagem_erro'] = 'Selecione um registro!'
        return

    # selecionando registro
    linha = linha_selecionada.iloc[0].copy()
    id_linha = int(linha['Id'])

    # montando a query e parametros
    query = text(SELECT_PROJECAO)
    parametro = {'id': id_linha}

    # importando dataframe
    try:
        df = listar_projecao(query, engine, parametro)
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar a projeção. ({e})'
        return

    if df.empty:
        st.session_state['mensagem_erro'] = 'Projeção não encontrada para o contrato selecionado.'
        return

    # formatando data
    df['Data de Vencimento'] = pd.to_datetime(df['Data de Vencimento'], format='%d/%m/%Y', errors='coerce').dt.strftime('%d/%m/%Y')
    df['Valor'] = df['Valor'].map(transformar_float_em_str)

    # visualizando df
    modal_projecao_valores(df, linha)

def deletar_contrato_banco(id_contrato):
    '''Registrando exclusão no banco de dados.'''

    # iniciando exclusão
    try:

        # definindo query e parametro
        query = text(DELETE_CONTRATO)
        parametro = {'id': id_contrato}

        # iniciando engine e chaando a função de interação com banco de dados
        # (o DELETE ... RETURNING devolve o contrato excluído, gravado no log na mesma transação)
        with engine.begin() as conn:
            contrato_excluido = interacao_database(query, conn, parametro).mappings().first()
            registrar_log(CONTRATO_EXCLUIR, 'contratos', id_contrato,
                          sucesso=contrato_excluido is not None,
                          detalhes=dict(contrato_excluido) if contrato_excluido else {'erro': 'contrato não encontrado'},
                          conn=conn)

        # registrando notificação e encerrando
        st.session_state['mensagem_sucesso'] = 'Contrato excluído com sucesso!'

    except Exception as e:
        registrar_log_falha(CONTRATO_EXCLUIR, getattr(e, 'orig', e), 'contratos', id_contrato)
        raise ValueError('Erro ao excluir contrato!')