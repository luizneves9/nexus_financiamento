import base64
import uuid
import streamlit as st

def visualizar_pdf(conteudo, altura=650):
    '''Exibe um PDF na tela com o visualizador nativo do navegador (zoom, páginas e impressão).

    O Chrome/Edge bloqueiam o visualizador de PDF dentro de iframes isolados (sandbox), como os do
    st.iframe/components. Por isso o PDF é montado na própria página: o st.html (com JavaScript) cria o
    iframe com um Blob do arquivo depois da limpeza de HTML do Streamlit (que remove iframes estáticos).
    Também oferece o link "Abrir em nova aba".
    '''

    identificador = f'pdf_{uuid.uuid4().hex}'
    conteudo_b64 = base64.b64encode(conteudo).decode('ascii')

    st.html(
        f"""
        <div id="{identificador}"></div>
        <script>
        (function () {{
            const area = document.getElementById("{identificador}");
            if (!area) return;
            try {{
                const binario = atob("{conteudo_b64}");
                const bytes = new Uint8Array(binario.length);
                for (let i = 0; i < binario.length; i++) bytes[i] = binario.charCodeAt(i);
                const url = URL.createObjectURL(new Blob([bytes], {{ type: 'application/pdf' }}));

                const quadro = document.createElement('iframe');
                quadro.src = url;
                quadro.title = 'Visualização do PDF';
                quadro.style.cssText = 'width:100%; height:{altura}px; border:1px solid rgba(128,128,128,.35); border-radius:8px;';
                area.appendChild(quadro);

                const link = document.createElement('a');
                link.href = url;
                link.target = '_blank';
                link.rel = 'noopener';
                link.textContent = 'Abrir em nova aba';
                link.style.cssText = 'display:inline-block; margin-top:6px; font-size:14px;';
                area.appendChild(link);
            }} catch (erro) {{
                area.textContent = 'Não foi possível exibir o PDF (' + erro.message + '). Use o botão Baixar.';
            }}
        }})();
        </script>
        """,
        unsafe_allow_javascript=True
    )
