import calendar
import pandas as pd
import streamlit as st
from datetime import date, datetime
from sqlalchemy import text
from database.connection import ConexaoBancoSQL
from queries.queries_outros_pagamentos import (
    SELECT_OUTROS_PAGAMENTOS,
    SELECT_OUTROS_PAGAMENTOS_POR_ID,
    INSERIR_OUTRO_PAGAMENTO,
    ALTERAR_OUTRO_PAGAMENTO,
    BAIXAR_OUTRO_PAGAMENTO,
    ESTORNAR_OUTRO_PAGAMENTO,
    EXCLUIR_OUTRO_PAGAMENTO,
)
from repositories.funcoes import ler_query
from repositories.contract import interacao_database
from services.log import (
    registrar_log,
    registrar_log_falha,
    OUTRO_PAGAMENTO_INCLUIR,
    OUTRO_PAGAMENTO_ALTERAR,
    OUTRO_PAGAMENTO_EXCLUIR,
    OUTRO_PAGAMENTO_BAIXAR,
    OUTRO_PAGAMENTO_ESTORNAR,
)

connect = ConexaoBancoSQL()
engine = connect.conexao_banco()

# modalidades (rótulo na tela -> valor no banco)
MODALIDADES = {'Compra Santo Anjo': 'COMPRA_SANTO_ANJO', 'Tributário': 'TRIBUTARIO'}
ROTULOS_MODALIDADE = {valor: rotulo for rotulo, valor in MODALIDADES.items()}

ENTIDADE = 'outros_pagamentos'

def listar_outros_pagamentos(modalidade=None, data_vcto_ini=None, data_vcto_fim=None, situacao=None):
    '''Parcelas de outros pagamentos com filtros opcionais (somente consulta).'''

    df = pd.DataFrame()
    parametros = {'modalidade': modalidade, 'data_vcto_ini': data_vcto_ini, 'data_vcto_fim': data_vcto_fim, 'situacao': situacao}
    try:
        with engine.begin() as conn:
            df = ler_query(text(SELECT_OUTROS_PAGAMENTOS), conn, parametros)
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar os outros pagamentos. ({e})'

    return df

def buscar_outros_pagamentos(ids):
    '''Parcelas pelos ids (dados atuais do banco, não da tabela formatada).'''

    df = pd.DataFrame()
    try:
        with engine.begin() as conn:
            df = ler_query(text(SELECT_OUTROS_PAGAMENTOS_POR_ID), conn, {'ids': [int(i) for i in ids]})
    except Exception as e:
        st.session_state['mensagem_erro'] = f'Erro ao consultar os outros pagamentos. ({e})'

    return df

def resumir_outros_pagamentos(df):
    '''Resumo antes da formatação: parcelas, total lançado, total pago e em aberto.'''

    abertas = df['situacao'] == 'ABERTA'
    return {
        'parcelas': len(df),
        'abertas': int(abertas.sum()),
        'pagas': int((~abertas).sum()),
        'valor': float(df['valor'].sum()),
        'valor_pago': float(df['valor_pago'].fillna(0).sum()),
        'valor_aberto': float(df.loc[abertas, 'valor'].sum())
    }

def somar_meses(data, meses):
    '''Mesma data `meses` à frente; dia inexistente no mês vira o último dia (31/01 + 1 = 28/02).'''

    mes_total = data.month - 1 + meses
    ano, mes = data.year + mes_total // 12, mes_total % 12 + 1
    return date(ano, mes, min(data.day, calendar.monthrange(ano, mes)[1]))

def gerar_parcelas(descricao, primeiro_vencimento, valor, quantidade):
    '''Prévia das parcelas mensais (mesmo dia; último dia do mês quando o dia não existe).'''

    quantidade = max(int(quantidade or 1), 1)
    linhas = []
    for numero in range(quantidade):
        complemento = f' - {numero + 1}/{quantidade}' if quantidade > 1 else ''
        linhas.append({
            'parcela': numero + 1,
            'descricao': f'{descricao or ""}{complemento}'.strip(' -') or None,
            'data_vencimento': somar_meses(primeiro_vencimento, numero),
            'valor': round(float(valor or 0), 2),
            'pago': False,
            'data_pagamento': None,
            'valor_pago': None
        })
    return pd.DataFrame(linhas)

def _texto(valor, tamanho):
    '''Texto limpo e cortado no tamanho da coluna (vazio -> None).'''
    valor = '' if valor is None or (isinstance(valor, float) and pd.isna(valor)) else str(valor).strip()
    return valor[:tamanho] or None

def _data(valor):
    '''Data do data_editor (date, Timestamp ou vazio) -> date ou None.'''
    if valor is None or pd.isna(valor):
        return None
    return valor.date() if isinstance(valor, datetime) else valor   # Timestamp/datetime -> date

def _valor(valor):
    '''Valor do data_editor -> float arredondado ou None.'''
    if valor is None or pd.isna(valor):
        return None
    return round(float(valor), 2)

def montar_itens_inclusao(df_editado):
    '''Itens da inclusão a partir da prévia editada; parcela não marcada como paga não leva baixa.'''

    itens = []
    for _, linha in df_editado.iterrows():
        pago = bool(linha.get('pago'))
        itens.append({
            'parcela': int(linha['parcela']),
            'descricao': _texto(linha.get('descricao'), 255),
            'data_vencimento': _data(linha.get('data_vencimento')),
            'valor': _valor(linha.get('valor')),
            'data_pagamento': _data(linha.get('data_pagamento')) if pago else None,
            'valor_pago': _valor(linha.get('valor_pago')) if pago else None,
            'pago': pago
        })
    return itens

def validar_inclusao(modalidade, itens):
    '''Mensagem de erro da inclusão ou None.'''

    if modalidade not in MODALIDADES.values():
        return 'Selecione a modalidade.'
    if not itens:
        return 'Nenhuma parcela para incluir.'

    for item in itens:
        if item['data_vencimento'] is None:
            return f'Informe o vencimento da parcela {item["parcela"]}.'
        if not item['valor'] or item['valor'] <= 0:
            return f'Informe um valor maior que zero na parcela {item["parcela"]}.'
        if item['pago'] and item['data_pagamento'] is None:
            return f'Informe a data de pagamento da parcela {item["parcela"]} (marcada como paga).'
        if item['pago'] and (not item['valor_pago'] or item['valor_pago'] <= 0):
            return f'Informe um valor pago maior que zero na parcela {item["parcela"]} (marcada como paga).'
    return None

def incluir_outros_pagamentos(modalidade, itens):
    '''Grava as parcelas numa única transação, com um log por parcela.'''

    usuario = st.session_state.get('auth_usuario')
    try:
        with engine.begin() as conn:
            for item in itens:
                parametros = {
                    'modalidade': modalidade,
                    'descricao': item['descricao'],
                    'data_vencimento': item['data_vencimento'],
                    'valor': item['valor'],
                    'data_pagamento': item['data_pagamento'],
                    'valor_pago': item['valor_pago'],
                    'usuario': usuario
                }
                id_registro = interacao_database(text(INSERIR_OUTRO_PAGAMENTO), conn, parametros).scalar()
                registrar_log(OUTRO_PAGAMENTO_INCLUIR, ENTIDADE, id_registro,
                              detalhes={k: v for k, v in parametros.items() if k != 'usuario'}, conn=conn)

        pagas = sum(1 for item in itens if item['pago'])
        st.session_state['mensagem_sucesso'] = (f'{len(itens)} parcela(s) de {ROTULOS_MODALIDADE[modalidade]} incluída(s)'
                                                f'{f" ({pagas} já paga(s))" if pagas else ""}.')
        return True

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(OUTRO_PAGAMENTO_INCLUIR, erro, ENTIDADE,
                            detalhes={'modalidade': modalidade, 'qtd_parcelas': len(itens)})
        st.session_state['mensagem_erro'] = f'Erro ao incluir as parcelas. ({erro})'
        return False

def validar_alteracao(modalidade, data_vencimento, valor):
    '''Mensagem de erro da alteração ou None.'''

    if modalidade not in MODALIDADES.values():
        return 'Selecione a modalidade.'
    if data_vencimento is None:
        return 'Informe o vencimento.'
    if not valor or valor <= 0:
        return 'Informe um valor maior que zero.'
    return None

def alterar_outro_pagamento(anterior, modalidade, descricao, data_vencimento, valor):
    '''Altera uma parcela em aberto, com log dos valores anteriores e novos.'''

    id_registro = int(anterior['id'])
    novo = {'modalidade': modalidade, 'descricao': _texto(descricao, 255), 'data_vencimento': data_vencimento,
            'valor': round(float(valor), 2)}
    detalhes = {
        'anterior': {campo: anterior[campo] for campo in novo},
        'novo': novo
    }

    try:
        with engine.begin() as conn:
            alterado = interacao_database(text(ALTERAR_OUTRO_PAGAMENTO), conn, {
                **novo, 'id': id_registro, 'usuario': st.session_state.get('auth_usuario')
            }).scalar()
            if alterado is None:
                raise ValueError('a parcela não está mais em aberto (atualize a tela).')
            registrar_log(OUTRO_PAGAMENTO_ALTERAR, ENTIDADE, id_registro, detalhes=detalhes, conn=conn)

        st.session_state['mensagem_sucesso'] = 'Parcela alterada.'
        return True

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(OUTRO_PAGAMENTO_ALTERAR, erro, ENTIDADE, id_registro, detalhes=detalhes)
        st.session_state['mensagem_erro'] = f'Erro ao alterar a parcela. ({erro})'
        return False

def montar_itens_baixa(df_editado):
    '''Itens da baixa (id, data e valor pago) a partir da tabela editada.'''

    return [{
        'id': int(linha['id']),
        'data_pagamento': _data(linha.get('data_pagamento')),
        'valor_pago': _valor(linha.get('valor_pago'))
    } for _, linha in df_editado.iterrows()]

def validar_baixa(itens):
    '''Mensagem de erro da baixa ou None.'''

    for item in itens:
        if item['data_pagamento'] is None:
            return 'Informe a data de pagamento de todas as parcelas.'
        if not item['valor_pago'] or item['valor_pago'] <= 0:
            return 'Informe um valor pago maior que zero em todas as parcelas.'
    return None

def baixar_outros_pagamentos(itens):
    '''Registra a baixa das parcelas em aberto numa única transação, com um log por parcela.'''

    usuario = st.session_state.get('auth_usuario')
    try:
        with engine.begin() as conn:
            for item in itens:
                baixado = interacao_database(text(BAIXAR_OUTRO_PAGAMENTO), conn, {**item, 'usuario': usuario}).scalar()
                if baixado is None:
                    raise ValueError(f'a parcela {item["id"]} não está mais em aberto (atualize a tela).')
                registrar_log(OUTRO_PAGAMENTO_BAIXAR, ENTIDADE, item['id'], detalhes=item, conn=conn)

        st.session_state['mensagem_sucesso'] = f'{len(itens)} parcela(s) baixada(s).'
        return True

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(OUTRO_PAGAMENTO_BAIXAR, erro, ENTIDADE, detalhes={'parcelas': itens})
        st.session_state['mensagem_erro'] = f'Erro ao baixar as parcelas. ({erro})'
        return False

def estornar_outros_pagamentos(ids):
    '''Estorna a baixa das parcelas pagas (limpa data e valor pago); o log guarda a baixa estornada.'''

    ids = [int(i) for i in ids]
    usuario = st.session_state.get('auth_usuario')
    try:
        with engine.begin() as conn:
            for id_registro in ids:
                estorno = interacao_database(text(ESTORNAR_OUTRO_PAGAMENTO), conn,
                                             {'id': id_registro, 'usuario': usuario}).mappings().first()
                if estorno is None:
                    raise ValueError(f'a parcela {id_registro} não está mais paga (atualize a tela).')
                registrar_log(OUTRO_PAGAMENTO_ESTORNAR, ENTIDADE, id_registro, detalhes=dict(estorno), conn=conn)

        st.session_state['mensagem_sucesso'] = f'{len(ids)} baixa(s) estornada(s).'
        return True

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(OUTRO_PAGAMENTO_ESTORNAR, erro, ENTIDADE, detalhes={'parcelas': ids})
        st.session_state['mensagem_erro'] = f'Erro ao estornar as baixas. ({erro})'
        return False

def excluir_outros_pagamentos(ids):
    '''Exclui parcelas em aberto; o log guarda a cópia de cada registro excluído.'''

    ids = [int(i) for i in ids]
    try:
        with engine.begin() as conn:
            for id_registro in ids:
                excluido = interacao_database(text(EXCLUIR_OUTRO_PAGAMENTO), conn, {'id': id_registro}).mappings().first()
                if excluido is None:
                    raise ValueError(f'a parcela {id_registro} não está mais em aberto (atualize a tela).')
                registrar_log(OUTRO_PAGAMENTO_EXCLUIR, ENTIDADE, id_registro, detalhes=dict(excluido), conn=conn)

        st.session_state['mensagem_sucesso'] = f'{len(ids)} parcela(s) excluída(s).'
        return True

    except Exception as e:
        erro = getattr(e, 'orig', e)
        registrar_log_falha(OUTRO_PAGAMENTO_EXCLUIR, erro, ENTIDADE, detalhes={'parcelas': ids})
        st.session_state['mensagem_erro'] = f'Erro ao excluir as parcelas. ({erro})'
        return False
