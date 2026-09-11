# Templaté de Rastreabilidade de Nova Funcionalidade

Use este roteiro para qualquer funcionalidade nova ou alteração relevante.
Copie o arquivo, substitua os campos e atualize o
[Registro de Status e Pendências](status-register.md), a matriz e o roadmap.

## 1. Identificação

- **ID da funcionalidade:** `RFXX`
- **Nome:**
- **Solicitante:**
- **Data:**
- **Responsavel tecnico:**
- **Prioridade:** Alta / Media / Baixa
- **Status inicial:** Planejado

## 2. Objetivo

Descreva qual problema a funcionalidade resolve e qual resultado o usuário
espera obter.

## 3. Escopo

### Incluido

- 

### Não incluído

- 

## 4. Requisitos e regras

- **Requisito funcional:** `RFXX`
- **Regras de negócio:** `RNXX`, `RNXX`
- **Requisitos não funcionais:** `RNFXX`, `RNFXX`

## 5. Use Case

- **Use Case:** `UCXX - Nome`
- **Ator principal:**
- **Pre-condicoes:**
- **Pos-condicoes:**
- **Fluxo principal:**
- **Fluxos alternativos:**
- **Exceções:**

## 6. Impacto tecnico

| Area | Impacto? | Arquivo ou objeto | Alteração necessaria |
| --- | --- | --- | --- |
| Interface | Sim / Não | `src/views/...` | |
| Service | Sim / Não | `src/services/...` | |
| Repository | Sim / Não | `src/repositories/...` | |
| Query | Sim / Não | `src/queries/...` | |
| Banco | Sim / Não | tabela, função, trigger ou view | |
| Calculo financeiro | Sim / Não | documento de cálculo | |
| Segurança | Sim / Não | perfil, permissão ou auditoria | |
| Operação | Sim / Não | deploy, backup ou monitoramento | |

## 7. O que já existe

- **Codigo:**
- **Banco:**
- **Documentação:**
- **Testes:**

## 8. O que falta

| ID | Pendência | Responsavel | Dependência | Critério de conclusão |
| --- | --- | --- | --- | --- |
| BL-XXX | | | | |

## 9. Critérios de aceite

- [ ] Fluxo principal funciona.
- [ ] Validacoes funcionam.
- [ ] Exceções foram tratadas.
- [ ] Persistencia foi validada.
- [ ] Cálculos foram validados, quando aplicável.
- [ ] Segurança foi revisada.
- [ ] Testes foram executados.
- [ ] Documentação foi atualizada.
- [ ] Responsavel do negócio aprovou.

## 10. Evidências

- **Arquivos de código:**
- **Objetos do banco:**
- **Testes:**
- **Commit ou release:**
- **Aprovação:**

## 11. Atualização do status

- **Status atual:**
- **Motivo:**
- **Próxima ação:**
- **Data da última revisão:**
