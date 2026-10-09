# Instalação e Implantação

## Requisitos

- Docker e Docker Compose.
- Imagem base `fin-base:1.0` disponível no ambiente, com Streamlit 1.63.0
  (o CSS da identidade visual depende dessa versão, DA07/BL-025):
  `docker run --rm --entrypoint python fin-base:1.0 -c "import streamlit; print(streamlit.__version__)"`.
- PostgreSQL acessivel pela rede do container.
- DDL e objetos do schema `financiamento` criados no banco.
- Arquivo `.env` configurado fora do controle de versão.

## Variaveis de ambiente

| Variavel | Finalidade |
| --- | --- |
| `DB_USER` | Usuario do PostgreSQL. |
| `DB_PASS` | Senha do PostgreSQL. |
| `DB_HOST` | Host do PostgreSQL. |
| `DB_PORT` | Porta do PostgreSQL. |
| `DB_NAME` | Nome do banco. |
| `AUTH_SECRET` | Chave que assina o cookie de login (valor aleatório longo, ex.: `python -c "import secrets; print(secrets.token_hex(32))"`). Sem ela, o login não persiste ao fechar o navegador. Trocar a chave derruba todas as sessões. |
| `TZ` | Fuso horario do container; atualmente `America/Sao_Paulo`. |

## Execução com Compose

Antes de iniciar a aplicação, confirme que o PostgreSQL possui o schema
`financiamento`, suas funções auxiliares, views e materialized views, e as
tabelas `usuarios` e `log_auditoria` (scripts `database/usuarios.sql` e
`database/log_auditoria.sql`, nessa ordem), com ao menos um usuário criado. Os
arquivos em `database/` documentam o estado do banco. O DDL exportado não deve
ser tratado como instalador ou migração automática; as funções de projeção
devem estar criadas no banco conforme o procedimento técnico validado.

```bash
docker compose up --build
```

A aplicação e publicada na porta `8502` e executa:

```bash
streamlit run src/main.py --server.port=8502 --server.address=0.0.0.0 --client.toolbarMode=viewer
```

O comando roda a partir de `/app` (raiz do repositório), de onde o Streamlit
lê `.streamlit/config.toml`. Alterações nesse arquivo exigem novo build e
reinício do container.

## Rede

O Compose utiliza a rede externa `rede-proxy` alem da rede padrão. A rede deve
existir antes da inicialização quando essa configuração for mantida.

## Verificacoes pos-implantação

1. Confirmar que o container iniciou sem erro.
2. Acessar a porta 8502 e fazer login (primeiro acesso: senha vazia e
   cadastro da senha).
2.1. Conferir o registro `LOGIN` em `financiamento.log_auditoria`.
3. Consultar empresas, bancos e fornecedores.
4. Consultar contratos.
5. Testar inclusão em ambiente controlado.
6. Testar projeção de um contrato conhecido.
7. Confirmar conectividade e logs do banco.
8. Conferir a identidade visual (DA07) nos temas claro e escuro: logo no
   login e no menu, destaque índigo e menu ⋮ só com Settings, Print e About.

## Promocao

A implantação em producao depende de: resolver BL-014 (segredos fora do
Git e rotacionados) e BL-015 (HTTPS), perfis de acesso, backup,
observabilidade, validação do DDL e aprovação dos testes de cálculo.
