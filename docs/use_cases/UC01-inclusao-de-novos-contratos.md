# UC01 – Inclusão de Novos Contratos

* **Ator Principal:** Usuário do Setor Financeiro
* **Requisitos Associados:** RF02.1, RF02.2, RN01
* **Pré-condições:** 
  1. Usuário autenticado e com permissão de escrita no módulo financeiro.
  2. Tabelas de Empresas, Bancos e Fornecedores cadastradas previamente.

---

## Fluxo Principal (FP)

1. O usuário acessa a interface web de inclusão de contratos.
2. O usuário preenche os campos obrigatórios do contrato (Empresa, Banco, N° Contrato, Valores, Taxas, Prazos) e vincula o(s) bem(ns)/veículo(s).
3. O usuário aciona a opção "Salvar".
4. O sistema executa o motor de cálculo, gerando a projeção automática das parcelas e seus vencimentos (`projecao_moeda` e `projecao_real`).
5. O sistema persiste as informações no banco de dados.
6. O sistema exibe uma mensagem de sucesso ao usuário e redireciona para a tela de detalhamento do contrato.

---

## Fluxos Alternativos (FA)

### FA01 – Projeção Prévia
* **Ponto de Origem:** Passo 2 do FP.
* **Gatilho:** O usuário deseja conferir as parcelas projetadas antes de salvar formalmente.
1. O usuário clica no botão "Projetar / Simular".
2. O sistema valida temporariamente os dados digitados e calcula a projeção em memória.
3. O sistema exibe uma modal com a tabela de projeção prévia de valores e parcelas.
4. O usuário analisa a tabela e clica no botão "Fechar".
5. O caso de uso retorna ao Passo 2 do Fluxo Principal.

### FA02 – Download em CSV da Projeção Prévia
* **Ponto de Origem:** Passo 3 do FA01.
* **Gatilho:** O usuário solicita o download do relatório projetado.
1. Na modal de projeção prévia, o usuário clica em "Exportar CSV".
2. O sistema gera o arquivo em formato `.csv` com base no Dataframe de cálculo atual e dispara o download no navegador.
3. O fluxo alternativo se encerra, mantendo a modal aberta ou retornando ao FA01.

---

## Fluxos de Exceção (FE)

### FE01 – Campos Obrigatórios Não Preenchidos
* **Ponto de Origem:** Passo 3 do FP ou Passo 1 do FA01.
* **Condição:** Um ou mais campos obrigatórios não foram informados.
1. O sistema destaca visualmente os campos inconsistentes.
2. O sistema exibe a mensagem de erro: *"Sem preenchimento de campos obrigatórios."*
3. O caso de uso retorna ao Passo 2 do FP.

### FE02 – Contrato Duplicado (RN01)
* **Ponto de Origem:** Passo 3 do FP.
* **Condição:** O `numero_contrato` informado já existe para o mesmo banco no sistema.
1. O sistema cancela a operação de gravação.
2. O sistema exibe a mensagem: *"Contrato já cadastrado no sistema."*
3. O caso de uso retorna ao Passo 2 do FP.

### FE03 – Falha na Comunicação com o Banco de Dados
* **Ponto de Origem:** Passo 5 do FP.
* **Condição:** Perda de conexão ou erro de infraestrutura na gravação.
1. O sistema exibe uma mensagem na tela: *"Falha ao se conectar com o banco de dados."*
2. O sistema registra o log detalhado de erro.
3. O caso de uso é encerrado sem salvar os dados.