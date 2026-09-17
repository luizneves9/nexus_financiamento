import streamlit as st
import pandas as pd
from services.relatorio_endividamento import listar_projecao_endividamento, transformar_dados_para_relatorio

st.set_page_config(layout="wide", page_title="Endividamento Bancário")

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


# ------------------------------------------------------------------
# MONTAGEM DO HTML ------------------------------------------------
# ------------------------------------------------------------------
def build_html(saldo, saldo_total_grupo, anos, tema):
    html = [get_css(tema)]
    html.append(
        "<div class='titulo-bar'><h2>ENDIVIDAMENTO BANCÁRIO - PROJEÇÃO DOS PAGAMENTOS - "
        "FLUXO DE CAIXA</h2></div>"
    )
    html.append("<table class='tabela-endiv'>")

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
            for v in linha["valores"]:
                html.append(f"<td class='body-row'>{fmt(v)}</td>")
            if i == 0:
                html.append(f"<td class='total-col' rowspan='{n}'>{fmt_total(bloco['total_grupo'])}</td>")
            html.append(f"<td class='total-anual'>{fmt_total(linha['total'])}</td>")
            html.append(f"<td class='pct-col'>{linha['pct']}</td>")
            html.append("</tr>")

    html.append("</table>")
    return "".join(html)


# ------------------------------------------------------------------
# RENDER ----------------------------------------------------------
# ------------------------------------------------------------------

# Buscar dados do banco
df_raw = listar_projecao_endividamento()

if not df_raw.empty:
    saldo, saldo_total_grupo, anos = transformar_dados_para_relatorio(df_raw)
    html_table = build_html(saldo, saldo_total_grupo, anos, st.session_state.tema_endividamento)
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
