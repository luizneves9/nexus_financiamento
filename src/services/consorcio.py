import io
import unicodedata
import pandas as pd
import streamlit as st
from datetime import datetime
from decimal import Decimal, InvalidOperation
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_consorcio import (
    SELECT_CONSORCIO_PAGO,
    SELECT_RESUMO_PAGO_PERIODO,
    EXCLUIR_PAGO_PERIODO,
    INSERIR_CONSORCIO_PAGO,
    SELECT_CONSORCIO_A_PAGAR,
    SELECT_RESUMO_A_PAGAR_COMPETENCIA,
    EXCLUIR_A_PAGAR_COMPETENCIA,
    INSERIR_CONSORCIO_A_PAGAR,
    SELECT_CONSORCIO_CREDITO,
    SELECT_CREDITO_COMPETENCIA,
    SALVAR_CONSORCIO_CREDITO,
    SELECT_CONSORCIADOS,
)
from repositories.funcoes import ler_query
from repositories.contract import interacao_database
from services.log import (
    registrar_log,
    registrar_log_falha,
    CONSORCIO_IMPORTAR_PAGO,
    CONSORCIO_IMPORTAR_A_PAGAR,
    CONSORCIO_CREDITO_SALVAR,
)

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

# tipos de importação
PAGO = 'PAGO'
A_PAGAR = 'A_PAGAR'

# colunas dos CSVs (nome normalizado: sem acento, minúsculo) -> (campo, tipo, obrigatório)
COLUNAS_PAGO = {
    'banco': ('banco', 'texto', True),
    'nome consorciado': ('nome_consorciado', 'texto', False),
    'numero proposta': ('numero_proposta', 'texto', True),
    'data adesao': ('data_adesao', 'data', False),
    'id cota': ('id_cota', 'texto', False),
    'nome codigo movimento financeiro': ('movimento', 'texto', True),
    'data pagamento': ('data_pagamento', 'data', True),
    'valor fundo comum': ('valor_fundo_comum', 'valor', False),
    'valor fundo reserva': ('valor_fundo_reserva', 'valor', False),
    'valor taxa administracao': ('valor_taxa_administracao', 'valor', False),
    'multa e juros': ('valor_multa_juros', 'valor', False),
    'outros': ('valor_outros', 'valor', False),
    'total': ('valor_total', 'valor', True),
}
COLUNAS_A_PAGAR = {
    'banco': ('banco', 'texto', True),
    'numero proposta': ('numero_proposta', 'texto', True),
    'valor parcela': ('valor_parcela', 'valor', True),
    'data pagamento': ('data_pagamento', 'data', True),
    'data emissao': ('data_emissao', 'data', False),
}

# tamanho máximo dos campos texto (database/consorcio_outros_pagamentos.sql)
TAMANHOS = {'banco': 100, 'nome_consorciado': 255, 'numero_proposta': 30, 'id_cota': 30, 'movimento': 100}

def competencia_do_mes(data):
    '''Competência gravada no banco: 1º dia do mês da data.'''
    return data.replace(day=1) if data else None

def _normalizar(nome):
    '''Nome de coluna sem acento, minúsculo e com espaços simples (evita falha por codificação do CSV).'''
    sem_acento = unicodedata.normalize('NFKD', str(nome)).encode('ascii', 'ignore').decode('ascii')
    return ' '.join(sem_acento.lower().split())

def _converter(valor, tipo):
    '''Converte o texto do CSV no tipo do campo (vazio -> None).'''

    valor = valor.strip()
    if not valor:
        return None
    if tipo == 'data':
        return datetime.strptime(valor, '%d/%m/%Y').date()
    if tipo == 'valor':
        return Decimal(valor.replace('.', '').replace(',', '.'))
    return valor

def ler_csv_consorcio(arquivo, tipo):
    '''Lê e valida o CSV de consórcio (';', formato brasileiro), pago ou a pagar.

    Devolve um dict com: linhas (lista de dicts), descartadas (linhas vazias), banco, consorciado (só no pago),
    data_ini, data_fim, total e erro (None quando o arquivo é válido). O arquivo deve ter um único banco e,
    no pago, um único consorciado (no a pagar o consorciado é informado na importação).
    '''

    colunas = COLUNAS_PAGO if tipo == PAGO else COLUNAS_A_PAGAR
    campo_valor = 'valor_total' if tipo == PAGO else 'valor_parcela'
    leitura = {'linhas': [], 'descartadas': 0, 'banco': None, 'consorciado': None, 'data_ini': None, 'data_fim': None, 'total': 0.0, 'erro': None}

    conteudo = arquivo.getvalue()
    try:
        texto = conteudo.decode('utf-8-sig')
    except UnicodeDecodeError:
        texto = conteudo.decode('cp1252')

    try:
        df = pd.read_csv(io.StringIO(texto), sep=';', dtype=str, keep_default_na=False)
    except Exception as e:
        leitura['erro'] = f'Não foi possível ler o arquivo. ({e})'
        return leitura

    # mapa coluna normalizada -> coluna original do arquivo
    originais = {_normalizar(coluna): coluna for coluna in df.columns}
    faltando = [nome for nome, (_, _, obrigatorio) in colunas.items() if obrigatorio and nome not in originais]
    if faltando:
        leitura['erro'] = f'Colunas obrigatórias não encontradas no arquivo: {", ".join(faltando)}.'
        return leitura

    linhas, erros = [], []
    for indice, registro in df.iterrows():
        numero_linha = indice + 2  # linha 1 é o cabeçalho
        if not any(str(v).strip() for v in registro.values):
            leitura['descartadas'] += 1   # linha vazia (só ';')
            continue

        try:
            linha = {}
            for nome, (campo, tipo_campo, obrigatorio) in colunas.items():
                valor = _converter(str(registro[originais[nome]]), tipo_campo) if nome in originais else None
                if obrigatorio and valor is None:
                    raise ValueError(campo)
                if tipo_campo == 'texto' and valor is not None:
                    valor = valor[:TAMANHOS[campo]]
                linha[campo] = valor
            linhas.append(linha)
        except (ValueError, InvalidOperation):
            erros.append(str(numero_linha))

    if erros:
        leitura['erro'] = (f'Data ou valor inválido (ou campo obrigatório vazio) nas linhas: '
                           f'{", ".join(erros[:10])}{"..." if len(erros) > 10 else ""}.')
        return leitura

    if not linhas:
        leitura['erro'] = 'Nenhuma linha preenchida encontrada no arquivo.'
        return leitura

    bancos = sorted({linha['banco'] for linha in linhas})
    if len(bancos) > 1:
        leitura['erro'] = f'O arquivo deve ter um único banco (encontrados: {", ".join(bancos)}). Separe um arquivo por banco.'
        return leitura

    consorciado = None
    if tipo == PAGO:
        consorciados = sorted({linha['nome_consorciado'] or '' for linha in linhas})
        if '' in consorciados:
            leitura['erro'] = 'Há linhas sem Nome Consorciado no arquivo.'
            return leitura
        if len(consorciados) > 1:
            leitura['erro'] = (f'O arquivo deve ter um único consorciado (encontrados: {", ".join(consorciados)}). '
                               f'Separe um arquivo por consorciado.')
            return leitura
        consorciado = consorciados[0]

    datas = [linha['data_pagamento'] for linha in linhas]
    leitura.update({
        'consorciado': consorciado,
        'linhas': linhas,
        'banco': bancos[0],
        'data_ini': min(datas),
        'data_fim': max(datas),
        'total': float(sum(linha[campo_valor] for linha in linhas))
    })
    return leitura

def _consultar(query, parametros, descricao):
    '''Leitura simples com tratamento de erro padrão.'''

    df = pd.DataFrame()
    try:
        with engine.begin() as conn:
            df = ler_query(text(query), conn, parametros)
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar {descricao}. ({e})'
    return df

def _filtro_texto(valor):
    '''Filtro de texto parcial (ILIKE) ou None.'''
    return f'%{valor}%' if valor else None

def listar_consorcio_pago(data_ini=None, data_fim=None, banco=None, consorciado=None, proposta=None):
    '''Pagamentos de consórcio pelo período da data de pagamento (somente consulta).'''
    return _consultar(SELECT_CONSORCIO_PAGO, {
        'data_ini': data_ini, 'data_fim': data_fim, 'banco': _filtro_texto(banco),
        'consorciado': _filtro_texto(consorciado), 'proposta': _filtro_texto(proposta)
    }, 'os pagamentos de consórcio')

def listar_consorcio_a_pagar(competencia, banco=None, consorciado=None, proposta=None):
    '''Parcelas a pagar de consórcio de uma competência (somente consulta).'''
    return _consultar(SELECT_CONSORCIO_A_PAGAR, {
        'competencia': competencia_do_mes(competencia), 'banco': _filtro_texto(banco),
        'consorciado': _filtro_texto(consorciado), 'proposta': _filtro_texto(proposta)
    }, 'as parcelas a pagar de consórcio')

def listar_consorciados():
    '''Nomes de consorciados já importados (pago ou a pagar), para o campo Consorciado do a pagar.'''
    df = _consultar(SELECT_CONSORCIADOS, {}, 'os consorciados')
    return [] if df.empty else df['nome_consorciado'].to_list()

def listar_consorcio_credito():
    '''Créditos de consórcio lançados por competência (somente consulta).'''
    return _consultar(SELECT_CONSORCIO_CREDITO, {}, 'os créditos de consórcio')

def buscar_credito(competencia):
    '''Lançamento de créditos da competência (dict) ou None.'''

    df = _consultar(SELECT_CREDITO_COMPETENCIA, {'competencia': competencia_do_mes(competencia)}, 'os créditos de consórcio')
    return None if df.empty else df.iloc[0].to_dict()

def _parametros_substituicao(tipo, leitura, competencia=None, consorciado=None):
    '''Chave do que a importação substitui: pago = banco + consorciado + período do arquivo;
    a pagar = competência + banco + consorciado informado.'''

    if tipo == PAGO:
        return {'banco': leitura['banco'], 'nome_consorciado': leitura['consorciado'],
                'data_ini': leitura['data_ini'], 'data_fim': leitura['data_fim']}
    return {'banco': leitura['banco'], 'nome_consorciado': consorciado, 'competencia': competencia_do_mes(competencia)}

def resumir_substituicao(tipo, leitura, competencia=None, consorciado=None):
    '''Quantidade e total já gravados que serão substituídos pela importação (dict qtd/total).'''

    query = SELECT_RESUMO_PAGO_PERIODO if tipo == PAGO else SELECT_RESUMO_A_PAGAR_COMPETENCIA
    parametros = _parametros_substituicao(tipo, leitura, competencia, consorciado)

    df = _consultar(query, parametros, 'os dados já importados')
    if df.empty:
        return {'qtd': 0, 'total': 0.0}
    return {'qtd': int(df.iloc[0]['qtd']), 'total': float(df.iloc[0]['total'])}

def importar_consorcio(tipo, leitura, nome_arquivo, competencia=None, consorciado=None):
    '''Grava o CSV numa única transação: apaga o que ele substitui e insere as linhas, com log.

    - Pago: substitui os pagamentos do banco + consorciado entre a menor e a maior data de pagamento do
      arquivo; a competência gravada é só referência (mês da maior data de pagamento).
    - A pagar: substitui a foto da competência (data base informada) para o banco do arquivo e o
      consorciado informado (gravado em todas as linhas).
    '''

    usuario = st.session_state.get('auth_usuario')
    if tipo == PAGO:
        acao, entidade = CONSORCIO_IMPORTAR_PAGO, 'consorcio_pago'
        competencia = competencia_do_mes(leitura['data_fim'])
        consorciado = leitura['consorciado']
        query_resumo, query_exclusao, query_insercao = SELECT_RESUMO_PAGO_PERIODO, EXCLUIR_PAGO_PERIODO, INSERIR_CONSORCIO_PAGO
    else:
        acao, entidade = CONSORCIO_IMPORTAR_A_PAGAR, 'consorcio_a_pagar'
        competencia = competencia_do_mes(competencia)
        consorciado = (consorciado or '').strip()[:255] or None
        if not consorciado:
            st.session_state['mensagem_erro'] = 'Informe o consorciado do arquivo a pagar.'
            return False
        query_resumo, query_exclusao, query_insercao = (SELECT_RESUMO_A_PAGAR_COMPETENCIA, EXCLUIR_A_PAGAR_COMPETENCIA,
                                                        INSERIR_CONSORCIO_A_PAGAR)
    parametros_exclusao = _parametros_substituicao(tipo, leitura, competencia, consorciado)

    detalhes = {
        'arquivo': nome_arquivo,
        'banco': leitura['banco'],
        'consorciado': consorciado,
        'competencia': competencia,
        'data_pagamento_ini': leitura['data_ini'],
        'data_pagamento_fim': leitura['data_fim'],
        'qtd_linhas': len(leitura['linhas']),
        'linhas_vazias_descartadas': leitura['descartadas'],
        'total': leitura['total']
    }

    try:
        with engine.begin() as conn:
            substituido = conn.execute(text(query_resumo), parametros_exclusao).mappings().first()
            interacao_database(text(query_exclusao), conn, parametros_exclusao)
            interacao_database(text(query_insercao), conn, [
                {**linha, 'nome_consorciado': consorciado, 'competencia': competencia, 'nome_arquivo': nome_arquivo, 'usuario': usuario}
                for linha in leitura['linhas']
            ])

            detalhes['substituidos_qtd'] = int(substituido['qtd'])
            detalhes['substituidos_total'] = float(substituido['total'])
            registrar_log(acao, entidade, None, detalhes=detalhes, conn=conn)

        descricao = 'pagamento(s)' if tipo == PAGO else 'parcela(s) a pagar'
        st.session_state['mensagem_sucesso'] = (f'{len(leitura["linhas"])} {descricao} de consórcio importado(s) '
                                                f'({leitura["banco"]} / {consorciado}); {detalhes["substituidos_qtd"]} substituído(s).')
        return True

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(acao, erro, entidade, detalhes=detalhes)
        st.session_state['mensagem_erro'] = f'Erro ao importar o consórcio. ({erro})'
        return False

def salvar_credito(competencia, credito_cotas_contempladas, credito_parcelas_nao_contempladas):
    '''Inclui ou atualiza os créditos da competência (um lançamento por mês), com log dos valores anteriores.'''

    competencia = competencia_do_mes(competencia)
    anterior = buscar_credito(competencia)
    parametros = {
        'competencia': competencia,
        'credito_cotas_contempladas': credito_cotas_contempladas,
        'credito_parcelas_nao_contempladas': credito_parcelas_nao_contempladas,
        'usuario': st.session_state.get('auth_usuario')
    }
    detalhes = {
        'competencia': competencia,
        'credito_cotas_contempladas': credito_cotas_contempladas,
        'credito_parcelas_nao_contempladas': credito_parcelas_nao_contempladas,
        'anterior': {
            'credito_cotas_contempladas': float(anterior['credito_cotas_contempladas']),
            'credito_parcelas_nao_contempladas': float(anterior['credito_parcelas_nao_contempladas'])
        } if anterior else None
    }

    try:
        with engine.begin() as conn:
            id_credito = interacao_database(text(SALVAR_CONSORCIO_CREDITO), conn, parametros).scalar()
            registrar_log(CONSORCIO_CREDITO_SALVAR, 'consorcio_credito', id_credito, detalhes=detalhes, conn=conn)

        st.session_state['mensagem_sucesso'] = f'Créditos de consórcio de {competencia:%m/%Y} salvos.'
        return True

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(CONSORCIO_CREDITO_SALVAR, erro, 'consorcio_credito', detalhes=detalhes)
        st.session_state['mensagem_erro'] = f'Erro ao salvar os créditos de consórcio. ({erro})'
        return False
