import base64
import json
import streamlit as st
import pandas as pd
from datetime import date
from services.relatorio_endividamento import (
    listar_projecao_endividamento,
    buscar_credito_endividamento,
    transformar_dados_para_relatorio,
    montar_rodape,
    consultar_resumo_mes,
    montar_resumo_mes,
)
from views.components.cabecalho import cabecalho

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# Inicializar preferência de tema
if 'tema_endividamento' not in st.session_state:
    st.session_state.tema_endividamento = 'auto'


def fmt(v):
    """Formata número com 3 decimais e ponto como separador (ex.: 7.536); mês sem valor mostra 0.000."""
    return f"{(v or 0):,.3f}"


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
    .modalidade { background:#D8E4BC; text-align:left; font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .modalidade-normal { background:#D8E4BC; text-align:left; font-weight:normal; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
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
    .modalidade { background:#2f3b17; text-align:left; font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .modalidade-normal { background:#2f3b17; text-align:left; font-weight:normal; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
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
    .modalidade { background:#D8E4BC; text-align:left; font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .modalidade-normal { background:#D8E4BC; text-align:left; font-weight:normal; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
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
    .modalidade { background:#2f3b17; text-align:left; font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .modalidade-normal { background:#2f3b17; text-align:left; font-weight:normal; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
}
</style>
"""


# larguras fixas das colunas (Anos, Modalidades, 12 meses, Total Anual, Total Anual, %), iguais na
# tabela dos anos e na do Sub Total para que as colunas fiquem alinhadas
COLUNAS_TABELA = (
    "<colgroup><col style='width:4%'><col style='width:14%'>"
    + "<col style='width:4.9%'>" * len(MESES)
    + "<col style='width:7.2%'><col style='width:8%'><col style='width:8%'></colgroup>"
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

    base = (".tabela-endiv td.body-row, .tabela-endiv td.total-anual, .tabela-endiv td.pct-col, .tabela-endiv td.total-col "
            "{ text-align:right; font-variant-numeric:tabular-nums; } "
            ".tabela-endiv td.modalidade, .tabela-endiv td.modalidade-normal { text-align:left; font-weight:bold; } "
            ".tabela-endiv td.saldo-rotulo { white-space:nowrap; overflow:visible; } "
            ".legenda-endiv { margin-top:6px; font-size:13px; } "
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
def build_html(saldo, saldo_total_grupo, anos, subtotal, rodape, tema, data_base):
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
        # rótulo avança sobre Jan e Fev (vazios no saldo) para caber numa linha só
        html.append(f"<td class='modalidade saldo-rotulo' colspan='4'>Saldo Acumulado - {linha['modalidade']}</td>")
        html.append(f"<td class='body-row' colspan='{len(MESES) - 2}'></td>")
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

    # Bloco Sub Total (modalidades + Total Geral): meses somados em todos os anos exibidos, total,
    # total pago até a data base e total a pagar em colunas próprias (linhas com a mesma altura dos anos)
    html.append("<tr>")
    html.append("<th class='hdr' colspan='2'>Sub Total</th>")
    for m in MESES:
        html.append(f"<th class='hdr'>{m}</th>")
    html.append("<th class='total-col'>Total</th>")
    html.append("<th class='hdr'>Total pago</th>")
    html.append("<th class='hdr'>Total a pagar</th>")
    html.append("</tr>")
    for linha in subtotal:
        html.append("<tr>")
        html.append(f"<td class='body-row modalidade' colspan='2'>{linha['modalidade']}</td>")
        for v in linha["valores"]:
            html.append(f"<td class='body-row'>{fmt(v)}</td>")
        html.append(f"<td class='total-col'>{fmt_total(linha['total'])}</td>")
        html.append(f"<td class='total-anual'>{fmt_total(linha['total_pago'])}</td>")
        html.append(f"<td class='total-anual'>{fmt_total(linha['total_a_pagar'])}</td>")
        html.append("</tr>")

    html.append("</table>")

    # Rodapé: créditos de consórcio (competência da data base ou última anterior) e Dívida Líquida
    html.append("<div style='height:16px'></div>")
    html.append(f"<table class='tabela-endiv' style='table-layout:fixed'>{COLUNAS_TABELA}")
    competencia = f" ({rodape['competencia']:%m/%Y})" if rodape['competencia'] else " (sem lançamento)"
    linhas_rodape = [
        ('modalidade-normal', f"(-) Crédito Cotas Contempladas{competencia}", rodape['credito_cotas_contempladas']),
        ('modalidade-normal', f"(-) Crédito Parcelas pagas e não contempladas{competencia}",
         rodape['credito_parcelas_nao_contempladas']),
        ('modalidade', "Dívida Líquida (Total a pagar - créditos)", rodape['divida_liquida']),
    ]
    for classe, rotulo, valor in linhas_rodape:
        html.append("<tr>")
        # rótulo à esquerda (Anos até Total pago) e valor na última coluna (Total a pagar)
        html.append(f"<td class='body-row {classe}' colspan='{len(MESES) + 4}'>{rotulo}</td>")
        html.append(f"<td class='total-anual'>{fmt_total(valor)}</td>")
        html.append("</tr>")
    html.append("</table>")

    html.append(
        "<div class='legenda-endiv'><span class='pago'></span>Mês liquidado</div>"
    )
    return "".join(html)


# Resumo do mês: Período, Modalidade e as 6 colunas de valores
COLUNAS_RESUMO = (
    "<colgroup><col style='width:14%'><col style='width:20%'>"
    + "<col style='width:11%'>" * 6
    + "</colgroup>"
)


def build_html_resumo(resumo, tema, data_base):
    """Resumo do mês (variação do endividamento): saldo do mês anterior, movimentos do mês e saldo na data base."""

    html = [get_css(tema), get_css_pagamento(tema)]
    html.append(
        "<div style='height:16px'></div>"
        "<div class='titulo-bar'><h2>RESUMO DO MÊS - VARIAÇÃO DO ENDIVIDAMENTO - "
        f"DATA BASE {data_base:%d/%m/%Y}</h2></div>"
    )
    html.append(f"<table class='tabela-endiv' style='table-layout:fixed'>{COLUNAS_RESUMO}")
    html.append("<tr>")
    for titulo in ("Período", "Modalidade", "Saldo Inicial", "Juros", "Pgto Mês",
                   "Contrato Quitado", "Contrato Novo", "Saldo Final"):
        html.append(f"<th class='hdr'>{titulo}</th>")
    html.append("</tr>")

    colunas = ('saldo_inicial', 'juros', 'pgto_mes', 'quitado', 'novo', 'saldo_final')
    for i, linha in enumerate(resumo['linhas']):
        html.append("<tr>")
        if i == 0:
            html.append(f"<td class='anos-col' rowspan='{len(resumo['linhas'])}'>{resumo['periodo']}</td>")
        html.append(f"<td class='body-row modalidade-normal'>{linha['modalidade']}</td>")
        for coluna in colunas:
            classe = 'total-anual' if coluna == 'saldo_final' else 'body-row'
            html.append(f"<td class='{classe}'>{fmt(linha[coluna])}</td>")
        html.append("</tr>")

    total = resumo['total']
    html.append("<tr>")
    html.append("<td class='modalidade' colspan='2'>Total</td>")
    for coluna in colunas:
        html.append(f"<td class='total-anual'>{fmt_total(total[coluna])}</td>")
    html.append("</tr>")
    html.append("</table>")

    # créditos de consórcio (mesma competência do rodapé do relatório) e Dívida Líquida na data base
    html.append("<div style='height:16px'></div>")
    html.append(f"<table class='tabela-endiv' style='table-layout:fixed'>{COLUNAS_RESUMO}")
    competencia = f" ({resumo['competencia']:%m/%Y})" if resumo['competencia'] else " (sem lançamento)"
    linhas_rodape = [
        ('modalidade-normal', f"(-) Crédito Cotas Contempladas{competencia}", -resumo['credito_cotas_contempladas']),
        ('modalidade-normal', f"(-) Crédito Parcelas pagas e não contempladas{competencia}",
         -resumo['credito_parcelas_nao_contempladas']),
        ('modalidade', "Dívida Líquida (Saldo Final - créditos)", resumo['divida_liquida']),
    ]
    for classe, rotulo, valor in linhas_rodape:
        html.append("<tr>")
        html.append(f"<td class='body-row {classe}' colspan='7'>{rotulo}</td>")
        html.append(f"<td class='total-anual'>{fmt_total(valor)}</td>")
        html.append("</tr>")
    html.append("</table>")
    html.append(
        "<div class='legenda-endiv'>Saldo Inicial: a pagar no último dia do mês anterior · "
        "Juros: correção (Selic) e reajustes/novas contemplações de consórcio · "
        "Contrato Novo: contratos com data de contabilização no mês</div>"
    )
    return "".join(html)


# ------------------------------------------------------------------
# PDF (impressão do navegador) --------------------------------------
# ------------------------------------------------------------------
# A4 paisagem, fonte ajustada para as 17 colunas preencherem a largura numa página, cores de fundo mantidas na impressão
CSS_IMPRESSAO = """
<style>
    @page { size: A4 landscape; margin: 8mm; }
    html, body { margin:0; background:#fff; color:#000; font-family:'Segoe UI', sans-serif; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .tabela-endiv { font-size: 11px; }
    .tabela-endiv th, .tabela-endiv td { padding: 1px 4px; }
    .titulo-bar { padding: 5px; }
    .titulo-bar h2 { font-size: 16px; }
    .legenda-endiv { font-size: 11px; }
    tr { break-inside: avoid; page-break-inside: avoid; }
</style>
"""


def imprimir_pdf(html_relatorio, titulo):
    """Abre a janela de impressão do navegador só com o relatório (o usuário escolhe "Salvar como PDF").

    Não há biblioteca de PDF na imagem: o documento é montado num iframe oculto criado por JavaScript
    (o st.html remove iframes estáticos) e impresso; o título da página vira o nome sugerido do arquivo."""

    documento = (
        # CSS de impressão depois do relatório: sobrepõe o CSS da tabela (espaçamento e título)
        f"<!doctype html><html><head><meta charset='utf-8'><title>{titulo}</title></head>"
        f"<body>{html_relatorio}{CSS_IMPRESSAO}</body></html>"
    )
    # em base64: o st.html filtra o HTML com o DOMPurify, que descarta o <script> cujo texto contenha "<"
    conteudo = base64.b64encode(documento.encode('utf-8')).decode('ascii')

    st.html(
        f"""
        <div style="display:none"></div>
        <script>
        (function () {{
            const quadro = document.createElement('iframe');
            quadro.style.cssText = 'position:fixed; right:0; bottom:0; width:0; height:0; border:0;';
            document.body.appendChild(quadro);
            const doc = quadro.contentWindow.document;
            doc.open();
            const binario = atob("{conteudo}");
            const bytes = new Uint8Array(binario.length);
            for (let i = 0; i !== binario.length; i++) bytes[i] = binario.charCodeAt(i);
            doc.write(new TextDecoder('utf-8').decode(bytes));
            doc.close();
            setTimeout(function () {{
                const tituloPagina = document.title;
                document.title = {json.dumps(titulo)};   // nome sugerido do PDF
                quadro.contentWindow.focus();
                quadro.contentWindow.print();
                document.title = tituloPagina;
                setTimeout(function () {{ quadro.remove(); }}, 1000);
            }}, 300);
        }})();
        </script>
        """,
        unsafe_allow_javascript=True
    )


# ------------------------------------------------------------------
# RENDER ----------------------------------------------------------
# ------------------------------------------------------------------

# cabeçalho padrão da tela (ícone do grupo no menu)
cabecalho('Endividamento Bancário', 'Projeção dos pagamentos por ano e modalidade (financiamentos, Compra Santo Anjo, consórcios e tributário).', 'bar_chart')

# filtros (FE = Filtro Endividamento); padrão: data base hoje e vencimentos a partir de 01/01/2026
if 'fe_data_base' not in st.session_state:
    st.session_state['fe_data_base'] = date.today()
if 'fe_data_corte' not in st.session_state:
    st.session_state['fe_data_corte'] = date(2026, 1, 1)
# o widget usa key própria; passar value= dinâmico recria o widget e descarta o que foi digitado
if 'fe_data_base_input' not in st.session_state:
    st.session_state['fe_data_base_input'] = st.session_state['fe_data_base']
if 'fe_data_corte_input' not in st.session_state:
    st.session_state['fe_data_corte_input'] = st.session_state['fe_data_corte']

with st.form('endividamento_filtro'):
    with st.container(horizontal=True, vertical_alignment='bottom'):
        data_base = st.date_input('Data base', key='fe_data_base_input', format='DD/MM/YYYY')
        data_corte = st.date_input('Vencimentos a partir do mês de', key='fe_data_corte_input', format='DD/MM/YYYY')
        submitido = st.form_submit_button('Filtrar')

    if submitido:
        st.session_state['fe_data_base'] = data_base or date.today()
        st.session_state['fe_data_corte'] = data_corte

# PDF do Endividamento Bancário (sem o resumo do mês), sempre no tema claro
gerar_pdf = st.button('Gerar PDF', icon=':material/picture_as_pdf:',
                      help='Abre a impressão do Endividamento Bancário (sem o resumo do mês): escolha "Salvar como PDF".')

# Buscar dados do banco (financiamentos com a regra do Contas a Pagar; consórcio, Santo Anjo e tributário na data base)
data_base = st.session_state['fe_data_base']
with st.spinner('Consultando endividamento...'):
    df_raw = listar_projecao_endividamento(
        data_base,
        data_corte=st.session_state.get('fe_data_corte')
    )
    credito = buscar_credito_endividamento(data_base)

if not df_raw.empty:
    saldo, saldo_total_grupo, anos, subtotal = transformar_dados_para_relatorio(df_raw)
    rodape = montar_rodape(subtotal, credito)
    html_table = build_html(saldo, saldo_total_grupo, anos, subtotal, rodape, st.session_state.tema_endividamento, data_base)
    st.markdown(html_table, unsafe_allow_html=True)

    if gerar_pdf:
        imprimir_pdf(build_html(saldo, saldo_total_grupo, anos, subtotal, rodape, 'claro', data_base),
                     f'Endividamento Bancário - Data base {data_base:%d-%m-%Y}')

    # resumo do mês (variação): posição no último dia do mês anterior x posição na data base
    with st.spinner('Consultando o resumo do mês...'):
        consulta_resumo = consultar_resumo_mes(data_base, data_corte=st.session_state.get('fe_data_corte'))
    if consulta_resumo is not None:
        df_inicial, df_final, base_inicial = consulta_resumo
        resumo = montar_resumo_mes(df_inicial, df_final, base_inicial, data_base, rodape)
        st.markdown(build_html_resumo(resumo, st.session_state.tema_endividamento, data_base), unsafe_allow_html=True)
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
