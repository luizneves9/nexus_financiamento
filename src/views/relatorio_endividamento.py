import streamlit as st
import pandas as pd
from datetime import date
from services.relatorio_endividamento import listar_projecao_endividamento, transformar_dados_para_relatorio
from views.components.cabecalho import cabecalho

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# Inicializar preferência de tema
if 'tema_endividamento' not in st.session_state:
    st.session_state.tema_endividamento = 'auto'


def fmt(v):
    """Formata número com 3 decimais e ponto como separador (ex.: 7.536)."""
    if v is None or v == 0:
        return ""
    return f"{v:,.3f}"


def fmt_total(v):
    """Formata total com 3 decimais e ponto como separador."""
    return f"{v:,.3f}"


# ------------------------------------------------------------------
# CSS ---------------------------------------------------------
# ------------------------------------------------------------------
def get_css(tema):
    """Retorna CSS baseado no tema selecionado.

    - 'auto': respeita a preferência do sistema operacional do usuário
    - 'claro': força tema claro
    - 'escuro': força tema escuro
    """

    if tema == 'claro':
        return """
<style>
    .tabela-endiv { border-collapse: collapse; width: 100%; font-family: 'Segoe UI', sans-serif; }
    .tabela-endiv th, .tabela-endiv td { border: 1px solid #000; padding: 4px 6px; text-align: center; }
    .titulo-bar { background:#c9d2a3; color:#2f3520; text-align:center; padding:10px; }
    .titulo-bar h2 { margin:0; font-size:20px; }
    .hdr { background:#4F6228; color:#fff; font-weight:bold; }
    .total-col { background:#D8E4BC; font-weight:bold; }
    .total-anual { background:#D8E4BC; font-weight:bold; }
    .pct-col { background:#D8E4BC; font-weight:bold; }
    .anos-col { background:#D8E4BC; font-weight:bold; }
    .modalidade { background:#D8E4BC; text-align:left; font-weight:bold;}
    .modalidade-normal { background:#D8E4BC; text-align:left; font-weight:normal; }
</style>
"""
    elif tema == 'escuro':
        return """
<style>
    .tabela-endiv { background:#363636; border-collapse: collapse; width: 100%; font-family: 'Segoe UI', sans-serif; }
    .tabela-endiv th, .tabela-endiv td { border: 1px solid #000; padding: 4px 6px; text-align: center; }
    .titulo-bar { background:#2f3b17; text-align:center; padding:10px; }
    .titulo-bar h2 { margin:0; font-size:20px; }
    .hdr { background:#4F6228; color:#fff; font-weight:bold; }
    .total-col { background:#2f3b17; font-weight:bold; }
    .total-anual { background:#2f3b17; font-weight:bold; }
    .pct-col { background:#2f3b17; font-weight:bold; }
    .anos-col { background:#2f3b17; font-weight:bold; }
    .modalidade { background:#2f3b17; text-align:left; font-weight:bold;}
    .modalidade-normal { background:#2f3b17; text-align:left; font-weight:normal; }
</style>
"""
    else:  # auto - respeita preferência do sistema operacional
        return """
<style>
/* TEMA AUTOMÁTICO - Respeita preferência do sistema operacional do usuário */
@media (prefers-color-scheme: light) {
    .tabela-endiv { border-collapse: collapse; width: 100%; font-family: 'Segoe UI', sans-serif; }
    .tabela-endiv th, .tabela-endiv td { border: 1px solid #000; padding: 4px 6px; text-align: center; }
    .titulo-bar { text-align:center; padding:10px; }
    .titulo-bar h2 { margin:0; font-size:20px; }
    .hdr { background:#4F6228; color:#fff; font-weight:bold; }
    .total-col { background:#D8E4BC; font-weight:bold; }
    .total-anual { background:#D8E4BC; font-weight:bold; }
    .pct-col { background:#D8E4BC; font-weight:bold; }
    .anos-col { background:#D8E4BC; font-weight:bold; }
    .modalidade { background:#D8E4BC; text-align:left; font-weight:bold;}
    .modalidade-normal { background:#D8E4BC; text-align:left; font-weight:normal; }
}

@media (prefers-color-scheme: dark) {
    .tabela-endiv { background:#363636; border-collapse: collapse; width: 100%; font-family: 'Segoe UI', sans-serif; }
    .tabela-endiv th, .tabela-endiv td { border: 1px solid #000; padding: 4px 6px; text-align: center; }
    .titulo-bar { text-align:center; padding:10px; }
    .titulo-bar h2 { margin:0; font-size:20px; }
    .hdr { background:#4F6228; color:#fff; font-weight:bold; }
    .total-col { background:#2f3b17; font-weight:bold; }
    .total-anual { background:#2f3b17; font-weight:bold; }
    .pct-col { background:#2f3b17; font-weight:bold; }
    .anos-col { background:#2f3b17; font-weight:bold; }
    .modalidade { background:#2f3b17; text-align:left; font-weight:bold;}
    .modalidade-normal { background:#2f3b17; text-align:left; font-weight:normal; }
}
</style>
"""


# larguras fixas das colunas (Anos, Modalidades, 12 meses, Total Anual, Total Anual, %), iguais na
# tabela dos anos e na do Sub Total para que as colunas fiquem alinhadas
COLUNAS_TABELA = (
    "<colgroup><col style='width:4%'><col style='width:10%'>"
    + "<col style='width:5.3%'>" * len(MESES)
    + "<col style='width:6.4%'><col style='width:8%'><col style='width:8%'></colgroup>"
)

CORES_PAGAMENTO = {
    # tema: (mês todo liquidado, mês parcialmente liquidado) - verde do cabeçalho da tabela
    'claro': ('#4F6228', '#76933C'),
    'escuro': ('#4F6228', '#76933C'),
}


def get_css_pagamento(tema):
    """CSS das células de meses pagos (até a data base) e da legenda, conforme o tema."""

    def regras(pago, parcial):
        return (f".tabela-endiv td.pago {{ background:{pago}; color:#fff; }} "
                f".tabela-endiv td.parcial {{ background:{parcial}; color:#fff; }} "
                f".legenda-endiv span.pago {{ background:{pago}; }} "
                f".legenda-endiv span.parcial {{ background:{parcial}; }} ")

    base = (".legenda-endiv { margin-top:6px; font-size:13px; } "
            ".legenda-endiv span { display:inline-block; width:14px; height:14px; border:1px solid #000; "
            "vertical-align:middle; margin:0 4px 0 12px; } ")

    if tema in CORES_PAGAMENTO:
        return f"<style>{base}{regras(*CORES_PAGAMENTO[tema])}</style>"

    return (f"<style>{base}"
            f"@media (prefers-color-scheme: light) {{ {regras(*CORES_PAGAMENTO['claro'])} }} "
            f"@media (prefers-color-scheme: dark) {{ {regras(*CORES_PAGAMENTO['escuro'])} }}</style>")


# ------------------------------------------------------------------
# MONTAGEM DO HTML ------------------------------------------------
# ------------------------------------------------------------------
def build_html(saldo, saldo_total_grupo, anos, subtotal, tema, data_base):
    html = [get_css(tema), get_css_pagamento(tema)]
    html.append(
        "<div class='titulo-bar'><h2>ENDIVIDAMENTO BANCÁRIO - PROJEÇÃO DOS PAGAMENTOS - "
        f"FLUXO DE CAIXA - DATA BASE {data_base:%d/%m/%Y}</h2></div>"
    )
    html.append(f"<table class='tabela-endiv' style='table-layout:fixed'>{COLUNAS_TABELA}")

    # Cabeçalho linha 1
    html.append("<tr>")
    html.append("<th class='hdr' rowspan='2'>Anos</th>")
    html.append("<th class='hdr' rowspan='2'>Modalidades</th>")
    html.append(f"<th class='hdr' colspan='{len(MESES)}'>Meses</th>")
    html.append("<th class='total-col' rowspan='2'>Total<br>Anual</th>")
    html.append("<th class='hdr' rowspan='2' >Total Anual</th>")
    html.append("<th class='hdr' rowspan='2' >%</th>")
    html.append("</tr>")

    # Cabeçalho linha 2 (meses)
    html.append("<tr>")
    for m in MESES:
        html.append(f"<th class='hdr'>{m}</th>")
    html.append("</tr>")

    # Bloco Saldo Acumulado (Total Anual mesclado nas linhas)
    for i, linha in enumerate(saldo):
        html.append("<tr>")
        if i == 0:
            html.append(f"<td class='anos-col' rowspan='{len(saldo)}'>-</td>")
        html.append(f"<td class='body-row modalidade'>{linha['modalidade']}</td>")
        html.append(f"<td class='body-row' colspan='{len(MESES)}'></td>")
        if i == 0:
            html.append(f"<td class='total-col' rowspan='{len(saldo)}'>{fmt_total(saldo_total_grupo)}</td>")
        html.append(f"<td class='total-anual'>{fmt_total(linha['total'])}</td>")
        html.append(f"<td class='pct-col'>{linha['pct']}</td>")
        html.append("</tr>")

    # Blocos por ano (Anos e Total Anual mesclados nas linhas do ano)
    for ano, bloco in anos.items():
        n = len(bloco["linhas"])
        for i, linha in enumerate(bloco["linhas"]):
            html.append("<tr>")
            if i == 0:
                html.append(f"<td class='anos-col' rowspan='{n}'>{ano}</td>")
            html.append(f"<td class='body-row modalidade-normal'>{linha['modalidade']}</td>")
            for v, status in zip(linha["valores"], linha["status"]):
                classe = 'pago' if status else ''   # mês com parcela liquidada até a data base
                html.append(f"<td class='body-row {classe}'>{fmt(v)}</td>")
            if i == 0:
                html.append(f"<td class='total-col' rowspan='{n}'>{fmt_total(bloco['total_grupo'])}</td>")
            html.append(f"<td class='total-anual'>{fmt_total(linha['total'])}</td>")
            html.append(f"<td class='pct-col'>{linha['pct']}</td>")
            html.append("</tr>")

    # espaço entre os anos e o Sub Total: duas tabelas com as mesmas larguras de coluna, separadas
    # por um espaço com o fundo do sistema (Streamlit)
    html.append("</table>")
    html.append("<div style='height:16px'></div>")
    html.append(f"<table class='tabela-endiv' style='table-layout:fixed'>{COLUNAS_TABELA}")

    # Bloco Sub Total (modalidades + Total Geral): meses somados em todos os anos exibidos,
    # total, total pago até a data base e total a pagar
    for i, linha in enumerate(subtotal):
        classe_modalidade = 'modalidade' if linha['modalidade'] == 'Total Geral' else 'modalidade-normal'
        html.append("<tr>")
        if i == 0:
            html.append(f"<td class='anos-col' rowspan='{len(subtotal)}'>Sub<br>Total</td>")
        html.append(f"<td class='body-row {classe_modalidade}'>{linha['modalidade']}</td>")
        for v in linha["valores"]:
            html.append(f"<td class='body-row'>{fmt(v)}</td>")
        html.append(f"<td class='total-col'>{fmt_total(linha['total'])}</td>")
        # rótulo e valor na mesma célula (duas colunas mescladas), sem a linha divisória entre eles
        html.append(
            "<td class='total-anual' colspan='2' style='white-space:nowrap'>"
            "<div style='display:flex; justify-content:space-between; gap:8px'>"
            f"<span>Total pago:</span><span>{fmt_total(linha['total_pago'])}</span></div>"
            "<div style='display:flex; justify-content:space-between; gap:8px'>"
            f"<span>Total a pagar:</span><span>{fmt_total(linha['total_a_pagar'])}</span></div>"
            "</td>"
        )
        html.append("</tr>")

    html.append("</table>")
    html.append(
        "<div class='legenda-endiv'><span class='pago'></span>Mês liquidado</div>"
    )
    return "".join(html)


# ------------------------------------------------------------------
# RENDER ----------------------------------------------------------
# ------------------------------------------------------------------

# cabeçalho padrão da tela (ícone do grupo no menu)
cabecalho('Endividamento Bancário', 'Projeção dos pagamentos do endividamento bancário por ano e modalidade.', 'bar_chart')

# filtros (FE = Filtro Endividamento); padrão: data base hoje e vencimentos a partir de 01/01/2026
if 'fe_data_base' not in st.session_state:
    st.session_state['fe_data_base'] = date.today()
if 'fe_data_corte' not in st.session_state:
    st.session_state['fe_data_corte'] = date(2026, 1, 1)
if 'fe_empresa' not in st.session_state:
    st.session_state['fe_empresa'] = None
if 'fe_banco' not in st.session_state:
    st.session_state['fe_banco'] = None

# o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado
if 'fe_data_base_input' not in st.session_state:
    st.session_state['fe_data_base_input'] = st.session_state['fe_data_base']
if 'fe_data_corte_input' not in st.session_state:
    st.session_state['fe_data_corte_input'] = st.session_state['fe_data_corte']
if 'fe_empresa_input' not in st.session_state:
    st.session_state['fe_empresa_input'] = st.session_state['fe_empresa'] or ''
if 'fe_banco_input' not in st.session_state:
    st.session_state['fe_banco_input'] = st.session_state['fe_banco'] or ''

with st.form('endividamento_filtro'):
    with st.container(horizontal=True, vertical_alignment='bottom'):
        data_base = st.date_input('Data base', key='fe_data_base_input', format='DD/MM/YYYY')
        data_corte = st.date_input('Vencimentos a partir do mês de', key='fe_data_corte_input', format='DD/MM/YYYY')
        empresa = st.text_input('Empresa', key='fe_empresa_input')
        banco = st.text_input('Banco', key='fe_banco_input')
        submitido = st.form_submit_button('Filtrar')

    if submitido:
        st.session_state['fe_data_base'] = data_base or date.today()
        st.session_state['fe_data_corte'] = data_corte
        st.session_state['fe_empresa'] = empresa if empresa else None
        st.session_state['fe_banco'] = banco if banco else None

# Buscar dados do banco (mesma regra do Contas a Pagar: pago até a data base, projetado depois)
data_base = st.session_state['fe_data_base']
with st.spinner('Consultando endividamento...'):
    df_raw = listar_projecao_endividamento(
        data_base,
        data_corte=st.session_state.get('fe_data_corte'),
        empresa=st.session_state.get('fe_empresa'),
        banco=st.session_state.get('fe_banco')
    )

if not df_raw.empty:
    saldo, saldo_total_grupo, anos, subtotal = transformar_dados_para_relatorio(df_raw)
    html_table = build_html(saldo, saldo_total_grupo, anos, subtotal, st.session_state.tema_endividamento, data_base)
    st.markdown(html_table, unsafe_allow_html=True)
else:
    st.warning('Nenhum dado disponível para o endividamento.')

st.divider()

# Botão de alternância de tema
st.markdown('**Tema da tabela:**')
col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.2, 5])
with col1:
    if st.button('Automático', use_container_width=True, help='Usa o tema do Streamlit/Sistema'):
        st.session_state.tema_endividamento = 'auto'
with col2:
    if st.button('Claro', use_container_width=True):
        st.session_state.tema_endividamento = 'claro'
with col3:
    if st.button('Escuro', use_container_width=True):
        st.session_state.tema_endividamento = 'escuro'

# Notificações
if 'mensagem_sucesso' in st.session_state:
    st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

if 'mensagem_erro' in st.session_state:
    st.toast(st.session_state.pop('mensagem_erro'), icon='⚠️')
