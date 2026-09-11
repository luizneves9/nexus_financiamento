# Gestão de Versoes e Releases

## Identificação

Cada release deve possuir identificador, data, commit, alterações de código,
alterações de banco, resultado dos testes e responsável pela aprovação.

## Checklist de release

- Requisitos e Use Cases atualizados.
- Matriz de rastreabilidade revisada.
- DDL ou migracoes versionados.
- Testes de aplicação e banco executados.
- Imagem Docker construida.
- Variaveis de ambiente conferidas.
- Backup e rollback avaliados para alterações de banco.
- Alterações comúnicadas aos usuários afetados.
- Plano de monitoramento pos-release definido.

## Ambientes

Os ambientes de desenvolvimento, teste e producao devem possuir configuracoes
separadas. Dados reais não devem ser copiados para desenvolvimento sem
tratamento e autorização.

## Rollback

Uma release que altere cálculos ou persistência deve ter estratégia de
rollback documentada antes da implantação. Em alterações de banco, o rollback
pode exigir restauração de backup ou script reverso validado.
