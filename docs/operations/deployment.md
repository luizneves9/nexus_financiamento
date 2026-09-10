# Instalacao e Implantacao

## Requisitos

- Docker e Docker Compose.
- Imagem base `fin-base:1.0` disponivel no ambiente.
- PostgreSQL acessivel pela rede do container.
- DDL e objetos do schema `financiamento` criados no banco.
- Arquivo `.env` configurado fora do controle de versao.

## Variaveis de ambiente

| Variavel | Finalidade |
| --- | --- |
| `DB_USER` | Usuario do PostgreSQL. |
| `DB_PASS` | Senha do PostgreSQL. |
| `DB_HOST` | Host do PostgreSQL. |
| `DB_PORT` | Porta do PostgreSQL. |
| `DB_NAME` | Nome do banco. |
| `TZ` | Fuso horario do container; atualmente `America/Sao_Paulo`. |

## Execucao com Compose

```bash
docker compose up --build
```

A aplicacao e publicada na porta `8502` e executa:

```bash
streamlit run src/main.py --server.port=8502 --server.address=0.0.0.0
```

## Rede

O Compose utiliza a rede externa `rede-proxy` alem da rede padrao. A rede deve
existir antes da inicializacao quando essa configuracao for mantida.

## Verificacoes pos-implantacao

1. Confirmar que o container iniciou sem erro.
2. Acessar a porta 8502.
3. Consultar empresas, bancos e fornecedores.
4. Consultar contratos.
5. Testar inclusao em ambiente controlado.
6. Testar projecao de um contrato conhecido.
7. Confirmar conectividade e logs do banco.

## Promocao

A implantacao em producao depende de autenticacao, backup, observabilidade,
validacao do DDL e aprovacao dos testes de calculo.
