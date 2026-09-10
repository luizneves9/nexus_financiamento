# Roadmap

## Fase atual - Desenvolvimento

- Inclusao e consulta de contratos.
- Consulta de empresas, bancos e fornecedores.
- Visualizacao parcial de projecoes.
- Exclusao fisica de contratos.
- Estruturas de banco para Selic, bens, veiculos e antecipacao.

## Versao 1.0

- Completar cadastro e vinculo de bens e veiculos.
- Disponibilizar registro de antecipacoes.
- Disponibilizar liquidacao total e parcial com registro.
- Implementar autenticacao e perfis.
- Implementar filtros e detalhamento.
- Validar calculos com testes de banco e aceite do financeiro.
- Definir integracao da Selic por API ou job.

## Evolucoes posteriores

- Avaliar exclusao logica.
- Implementar auditoria completa.
- Definir aprovacao por perfil para ajustes e baixas.
- Formalizar backup, restauracao, RTO e RPO.
- Aprimorar regras de unicidade de chassi e placa.
- Automatizar atualizacao das materialized views apos operacoes relevantes.

## Criterio de conclusao da versao 1.0

A versao 1.0 sera considerada pronta quando os fluxos prioritarios estiverem
implementados na interface, persistidos corretamente, cobertos por testes,
protegidos por acesso adequado e aprovados pelo responsavel do negocio.
