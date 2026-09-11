# Instalação e Implantação

## Requisitos

- Docker e Docker Compose.
- Imagem base `fin-base:1.0` disponível no ambiente.
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
| `TZ` | Fuso horario do container; atualmente `America/Sao_Paulo`. |

## Execução com Compose

Antes de iniciar a aplicação, confirme que o PostgreSQL possui o schema
`financiamento`, suas funções auxiliares, views e materialized views. Os
arquivos em `database/` documentam o estado do banco. O DDL exportado não deve
ser tratado como instalador ou migração automática; as funções de projeção
devem estar criadas no banco conforme o procedimento técnico validado.

```bash
docker compose up --build
```

A aplicação e publicada na porta `8502` e executa:

```bash
streamlit run src/main.py --server.port=8502 --server.address=0.0.0.0
```

## Rede

O Compose utiliza a rede externa `rede-proxy` alem da rede padrão. A rede deve
existir antes da inicialização quando essa configuração for mantida.

## Verificacoes pos-implantação

1. Confirmar que o container iniciou sem erro.
2. Acessar a porta 8502.
3. Consultar empresas, bancos e fornecedores.
4. Consultar contratos.
5. Testar inclusão em ambiente controlado.
6. Testar projeção de um contrato conhecido.
7. Confirmar conectividade e logs do banco.

## Promocao

A implantação em producao depende de autenticação, backup, observabilidade,
validação do DDL e aprovação dos testes de cálculo.
